package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Components.Utils;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.Interfaces.ITextBox;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.Configuration.Configuration;
	import Elixys.JSON.State.Reagent;
	import Elixys.JSON.State.Sequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.events.FocusEvent;
	import flash.events.KeyboardEvent;
	import flash.events.MouseEvent;
	import flash.events.SoftKeyboardEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.getQualifiedClassName;

	// This cassette subview is an extension of the subview base class
	public class SubviewCassette extends SubviewBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewCassette(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, ComponentCassette.COMPONENTTYPE, nButtonWidth, VIEW_CASSETTE, 
				EDIT_CASSETTE, RUN_CASSETTE, attributes);
			m_nButtonWidth = nButtonWidth;
			
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				// Get references to the components and add event listeners
				m_pCassetteLabel = UILabel(findViewById("cassettelabel"));
				if (m_sMode == Constants.VIEW)
				{
					m_pReagentNameLabel = UILabel(findViewById("reagentnamelabel"));
					m_pReagentDescriptionLabel = UILabel(findViewById("reagentdescriptionlabel"));
				}
				else
				{
					m_pReagentNameInput = Input(findViewById("reagentnameinput"));
					m_pReagentNameTextBox = m_pReagentNameInput.inputField as ITextBox;
					ConfigureTextBox(m_pReagentNameTextBox);
					m_pReagentDescriptionInput = Input(findViewById("reagentdescriptioninput"));
					m_pReagentDescriptionTextBox = m_pReagentDescriptionInput.inputField as ITextBox;
					ConfigureTextBox(m_pReagentDescriptionTextBox);
				}
				m_pReagentContainer = Form(findViewById("reagentcontainer"));
				
				// Add event listeners
				addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
			}
		}
		
		/***
		 * Member functions
		 **/
		
		// Updates the component
		public override function UpdateComponent(pComponent:ComponentBase):void
		{
			// Call the base implementation
			super.UpdateComponent(pComponent);

			// Initialize when the configuration becomes available
			var nIndex:int;
			if ((m_pConfiguration == null) && (m_pElixys.GetConfiguration() != null))
			{
				// Create the buttons
				m_pConfiguration = m_pElixys.GetConfiguration();
				m_nButtonCount = m_pConfiguration.ReactorReagentPositions.length + m_pConfiguration.ReactorDeliveryPositions.length + 
					m_pConfiguration.ReactorElutePositions.length;
				for (nIndex = 0; nIndex < m_nButtonCount; ++nIndex)
				{
					// Create the skins
					m_pUpSkins.push(Utils.AddSkin(tools_btn_up, true, this, m_nButtonWidth));
					m_pDownSkins.push(Utils.AddSkin(tools_btn_down, true, this, m_nButtonWidth));
					m_pDisabledSkins.push(Utils.AddSkin(tools_btn_disabled, true, this, m_nButtonWidth));
					m_pActiveSkins.push(Utils.AddSkin(tools_btn_active, true, this, m_nButtonWidth));
					
					// Create the labels
					m_pLabels.push(Utils.AddLabel("", this, FONTFACE, FONTSIZE, Styling.AS3Color(Styling.TEXT_BLACK)));
					
					// Create an initial hit area
					m_pHitAreas.push(new Rectangle());
				}
				
				// Initialize the button positions
				AdjustPositions();
			}

			// We only are concerned with view and edit modes
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				// Remember the component
				m_pComponent = new ComponentCassette(null, pComponent);
				
				// Press or release the buttons
				for (nIndex = 0; nIndex < m_nButtonCount; ++nIndex)
				{
					if (nIndex == m_nPressedReagent)
					{
						PressButton(nIndex);
					}
					else
					{
						ReleaseButton(nIndex);
					}
				}
	
				// Adjust the positions and selected reagent
				AdjustPositions();
				SelectReagent(m_nSelectedReagent);
			}
		}
		
		// Adjust the component position
		protected function AdjustPositions():void
		{
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				// Update if our dimensions have changed
				var pReagentContainerPosition:Point = globalToLocal(m_pReagentContainer.localToGlobal(new Point(0, 0)));
				if ((m_pReagentContainer.attributes.width != m_nLastWidth) ||
					(m_pReagentContainer.attributes.height != m_nLastHeight))
				{
					// Calculate scaling, adjusting for the size of the buttons
					var nOffsetX:Number = pReagentContainerPosition.x + BUTTON_HORIZONTAL_GAP;
					var nOffsetY:Number = pReagentContainerPosition.y + BUTTON_VERTICAL_GAP;
					var nScaleX:Number = (m_pReagentContainer.attributes.width - (m_pUpSkins[0] as Sprite).width - (2 * BUTTON_HORIZONTAL_GAP)) / 
						m_pConfiguration.ReactorLayoutDimensions.x;
					var nScaleY:Number = (m_pReagentContainer.attributes.height - (m_pUpSkins[0] as Sprite).height - (2 * BUTTON_VERTICAL_GAP)) / 
						m_pConfiguration.ReactorLayoutDimensions.y;

					// Position each button
					var nIndex:int, nDeliveryIndex:int, nEluteIndex:int, pRawButtonPosition:Point, sLabel:String, pUpSkin:Sprite, pDownSkin:Sprite, 
						pActiveSkin:Sprite, pDisabledSkin:Sprite, pLabel:UILabel, pRectangle:Rectangle, nInputBottom:int = -1, nInputTop:int = -1, 
						nInputBottomIndex:int = 0, nInputTopIndex:int = 0;
					var pScaledButtonPosition:Point = new Point();
					for (nIndex = 0; nIndex < m_nButtonCount; ++nIndex)
					{
						// Determine the button position
						if (nIndex < m_pConfiguration.ReactorReagentPositions.length)
						{
							pRawButtonPosition = m_pConfiguration.ReactorReagentPositions[nIndex] as Point;
							sLabel = (nIndex + 1).toString();
						}
						else if (nIndex < (m_pConfiguration.ReactorReagentPositions.length + m_pConfiguration.ReactorDeliveryPositions.length))
						{
							nDeliveryIndex = nIndex - m_pConfiguration.ReactorReagentPositions.length;
							pRawButtonPosition = m_pConfiguration.ReactorDeliveryPositions[nDeliveryIndex] as Point;
							sLabel = "A" + (nDeliveryIndex + 1).toString();
						}
						else
						{
							nEluteIndex = nIndex - m_pConfiguration.ReactorReagentPositions.length - m_pConfiguration.ReactorDeliveryPositions.length;
							pRawButtonPosition = m_pConfiguration.ReactorElutePositions[nEluteIndex] as Point;
							sLabel = "E";
						}
						pScaledButtonPosition.x = pRawButtonPosition.x * nScaleX;
						pScaledButtonPosition.y = pRawButtonPosition.y * nScaleY;

						// Set the skin positions
						pUpSkin = m_pUpSkins[nIndex] as Sprite;
						pDownSkin = m_pDownSkins[nIndex] as Sprite;
						pActiveSkin = m_pActiveSkins[nIndex] as Sprite;
						pDisabledSkin = m_pDisabledSkins[nIndex] as Sprite;
						pUpSkin.x = pDownSkin.x = pActiveSkin.x = pDisabledSkin.x = pReagentContainerPosition.x + pScaledButtonPosition.x;
						pUpSkin.y = pDownSkin.y = pActiveSkin.y = pDisabledSkin.y = pReagentContainerPosition.y + pScaledButtonPosition.y;

						// Set the label text and position
						pLabel = m_pLabels[nIndex] as UILabel;
						pLabel.width = pUpSkin.width;
						pLabel.text = sLabel;
						pLabel.width = pLabel.textWidth + 5;
						pLabel.x = pUpSkin.x + ((pUpSkin.width - pLabel.width) / 2);
						pLabel.y = pUpSkin.y + ((pUpSkin.height - pLabel.height) / 2);
						
						// Set the hit area
						pRectangle = m_pHitAreas[nIndex] as Rectangle;
						pRectangle.x = pUpSkin.x;
						pRectangle.y = pUpSkin.y;
						pRectangle.width = pUpSkin.width;
						pRectangle.height = pUpSkin.height;

						// Update the input area of interest
						if ((nInputTop == -1) || (nInputTop > pUpSkin.y))
						{
							nInputTopIndex = nIndex;
							nInputTop = pUpSkin.y;
						}
						if ((nInputBottom == -1) || (nInputBottom < (pUpSkin.y + pUpSkin.height)))
						{
							nInputBottomIndex = nIndex;
							nInputBottom = pUpSkin.y + pUpSkin.height;
						}
					}

					// Update the input area of interest
					if ((nInputTop != -1) && (nInputBottom != -1))
					{
						m_nInputAreaOfInterestTop = (m_pUpSkins[nInputTopIndex] as Sprite).getBounds(stage).top;
						m_nInputAreaOfInterestBottom = (m_pUpSkins[nInputBottomIndex] as Sprite).getBounds(stage).bottom;
					}
					
					// Remember the new dimensions
					m_nLastWidth = m_pReagentContainer.attributes.width;
					m_nLastHeight = m_pReagentContainer.attributes.height;
				}
			}
		}

		// Selects the specified reagent
		protected function SelectReagent(nReagentIndex:int):void
		{
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				// Set the label, name and description
				m_pCassetteLabel.text = "CASSETTE " + m_pComponent.Reactor + " : VIAL " + (nReagentIndex + 1).toString();
				if (m_sMode == Constants.VIEW)
				{
					m_pReagentNameLabel.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Name;
					var nMaxTextWidth:Number = (m_pReagentDescriptionLabel.parent as Form).attributes.width;
					m_pReagentDescriptionLabel.width = nMaxTextWidth;
					m_pReagentDescriptionLabel.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Description;
					if (m_pReagentDescriptionLabel.textWidth > nMaxTextWidth)
					{
						AddEllipsis(m_pReagentDescriptionLabel, nMaxTextWidth);
					}
				}
				else
				{
					if (m_pKeyboardFocusTextBox != m_pReagentNameInput.inputField)
					{
						m_pReagentNameInput.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Name;
						m_pReagentNameTextBox.editable = true;
						m_pReagentNameTextBox.color = Styling.AS3Color(Styling.TEXT_BLACK);
					}
					if (m_pKeyboardFocusTextBox != m_pReagentDescriptionInput.inputField)
					{
						m_pReagentDescriptionInput.text = (m_pComponent.Reagents[nReagentIndex] as Reagent).Description;
						m_pReagentDescriptionTextBox.editable = true;
						m_pReagentDescriptionTextBox.color = Styling.AS3Color(Styling.TEXT_BLACK);
					}
				}
				
				// Select the new reagent
				var nOldReagent:int = m_nSelectedReagent;
				m_nSelectedReagent = nReagentIndex;
				ReleaseButton(nOldReagent);
				ReleaseButton(m_nSelectedReagent);
			}
		}

		
		// Presses the specified button
		protected function PressButton(nIndex:int):void
		{
			(m_pUpSkins[nIndex] as Sprite).visible = false;
			(m_pDownSkins[nIndex] as Sprite).visible = true;
			(m_pDisabledSkins[nIndex] as Sprite).visible = false;
			(m_pActiveSkins[nIndex] as Sprite).visible = false;
			(m_pLabels[nIndex] as UILabel).textColor = PRESSEDTEXTCOLOR;
		}
		
		// Release the specified button
		protected function ReleaseButton(nIndex:int):void
		{
			var bUpVisible:Boolean = false, bDownVisible:Boolean = false, bActiveVisible:Boolean = false,
				bDisabledVisible:Boolean = false, nTextColor:uint = 0;
			if (nIndex < m_pConfiguration.ReactorReagentPositions.length)
			{
				if (nIndex == m_nSelectedReagent)
				{
					bActiveVisible = true;
					nTextColor = ACTIVETEXTCOLOR;
				}
				else
				{
					bUpVisible = true;
					nTextColor = ENABLEDTEXTCOLOR;
				}
			}
			else
			{
				bDisabledVisible = true;
			}
			(m_pUpSkins[nIndex] as Sprite).visible = bUpVisible;
			(m_pDownSkins[nIndex] as Sprite).visible = bDownVisible;
			(m_pDisabledSkins[nIndex] as Sprite).visible = bDisabledVisible;
			(m_pActiveSkins[nIndex] as Sprite).visible = bActiveVisible;
			(m_pLabels[nIndex] as UILabel).textColor = nTextColor;
		}

		// Reduces the string width and adds ellipsis
		protected function AddEllipsis(pTextField:TextField, nMaxWidth:Number):void
		{
			if (pTextField.textWidth > nMaxWidth)
			{
				// Append the ellipsis
				pTextField.appendText("...");
				
				// Loop until the string is small enough
				while (pTextField.textWidth > nMaxWidth)
				{
					pTextField.replaceText(pTextField.text.length - 4, pTextField.text.length - 3, "");
				}
			}
		}

		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Check for button clicks
			for (var nIndex:int = 0; nIndex < m_nButtonCount; ++nIndex)
			{
				if ((m_pHitAreas[nIndex] as Rectangle).contains(mouseX, mouseY))
				{
					if ((m_pDisabledSkins[nIndex] as Sprite).visible == false)
					{
						// Press the button and wait for mouse up
						m_nPressedReagent = nIndex;
						PressButton(m_nPressedReagent);
						stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
					}
					break;
				}
			}
		}
		
		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener and release the button
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			ReleaseButton(m_nPressedReagent);
			
			// Check if the mouse was release over the same button that was initially clicked
			if ((m_pHitAreas[m_nPressedReagent] as Rectangle).contains(mouseX, mouseY))
			{
				// Select the reagent
				SelectReagent(m_nPressedReagent);
			}
			m_nPressedReagent = -1;
		}

		// Called when the user changes the text in one of our input fields
		protected override function OnTextValueChanged(pFocusTarget:ITextBox):void
		{
			// Copy and update the selected reagent
			var pSelectedReagent:Reagent = new Reagent();
			pSelectedReagent.Copy(m_pComponent.Reagents[m_nSelectedReagent] as Reagent);
			if (pFocusTarget == m_pReagentNameTextBox)
			{
				pSelectedReagent.Name = m_pReagentNameTextBox.text;
			}
			else if (pFocusTarget == m_pReagentDescriptionTextBox)
			{
				pSelectedReagent.Description = m_pReagentDescriptionTextBox.text;
			}
			
			// Post the reagent to the server
			PostReagent(pSelectedReagent);
		}

		/***
		 * Member variables
		 **/

		// View cassette XML
		protected static const VIEW_CASSETTE:XML = 
			<columns gapH="0" widths="6%,88%,6%">
				<frame />
				<rows background={Styling.APPLICATION_BACKGROUND} gapV="0" heights="2%,8%,10,18%,72%">
					<frame />
					<label id="cassettelabel" useEmbedded="true" alignH="left" alignV="centre">
						<font face="GothamBold" color={Styling.TEXT_BLUE2} size="16" />
					</label>
					<frame />
					<columns gapH="10" widths="17%,83%">
						<rows gapV="10">
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									NAME
								</font>
							</label>
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									DESCRIPTION
								</font>
							</label>
						</rows>
						<rows gapV="10">
							<label id="reagentnamelabel" useEmbedded="true" alignH="left" alignV="centre">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="16" />
							</label>
							<label id="reagentdescriptionlabel" useEmbedded="true" alignH="left" alignV="centre">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="16" />
							</label>
						</rows>
					</columns>
					<frame id="reagentcontainer" />
				</rows>
			</columns>;

		// Edit cassette XML
		protected static const EDIT_CASSETTE:XML = 
			<columns gapH="0" widths="6%,88%,6%">
				<frame />
				<rows background={Styling.APPLICATION_BACKGROUND} gapV="0" heights="2%,8%,10,18%,72%">
					<frame />
					<label id="cassettelabel" useEmbedded="true" alignH="left" alignV="centre">
						<font face="GothamBold" color={Styling.TEXT_BLUE2} size="16" />
					</label>
					<frame />
					<columns gapH="10" widths="17%,83%">
						<rows gapV="10">
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									NAME
								</font>
							</label>
							<label useEmbedded="true" alignH="right" alignV="centre">
								<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14">
									DESCRIPTION
								</font>
							</label>
						</rows>
						<rows gapV="10" heights="50%,50%">
							<frame alignH="fill">
								<input id="reagentnameinput" alignH="fill" color={Styling.TEXT_GRAY1} 
										size="22" skin={getQualifiedClassName(TextInput_upSkin)} 
										returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
							</frame>
							<frame alignH="fill">
								<input id="reagentdescriptioninput" alignH="fill" color={Styling.TEXT_GRAY1} 
										size="22" skin={getQualifiedClassName(TextInput_upSkin)} 
										returnKeyLabel={Constants.RETURNKEYLABEL_NEXT} />
							</frame>
						</rows>
					</columns>
					<frame id="reagentcontainer" />
				</rows>
			</columns>;

		// Run cassette XML
		protected static const RUN_CASSETTE:XML = 
			<frame />;
		
		// Cassette components
		protected var m_pCassetteLabel:UILabel;
		protected var m_pReagentNameLabel:UILabel;
		protected var m_pReagentDescriptionLabel:UILabel;
		protected var m_pReagentNameInput:Input;
		protected var m_pReagentNameTextBox:ITextBox;
		protected var m_pReagentDescriptionInput:Input;
		protected var m_pReagentDescriptionTextBox:ITextBox;
		protected var m_pReagentContainer:Form;

		// Cassette arrays go in the following order:
		// 1. Reagent buttons
		// 2. Delivery buttons
		// 3. Elute buttons
		protected var m_pConfiguration:Configuration;
		protected var m_nButtonCount:uint;
		protected var m_pUpSkins:Array = new Array();
		protected var m_pDownSkins:Array = new Array();
		protected var m_pDisabledSkins:Array = new Array();
		protected var m_pActiveSkins:Array = new Array();
		protected var m_pLabels:Array = new Array();
		protected var m_pHitAreas:Array = new Array();

		// Current cassette and selected reagent index
		protected var m_pComponent:ComponentCassette;
		protected var m_nSelectedReagent:int = 0;
		protected var m_nPressedReagent:int = -1;

		// Last know dimensions
		protected var m_nLastWidth:Number = 0;
		protected var m_nLastHeight:Number = 0;
		
		// Constants
		protected static const FONTFACE:String = "GothamBold";
		protected static const FONTSIZE:int = 34;
		protected static const ENABLEDTEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_GRAY2);
		protected static const DISABLEDTEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_GRAY7);
		protected static const ACTIVETEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_BLUE1);
		protected static const PRESSEDTEXTCOLOR:uint = Styling.AS3Color(Styling.TEXT_WHITE);
		protected static const BUTTON_HORIZONTAL_GAP:int = 10;
		protected static const BUTTON_VERTICAL_GAP:int = 10;
	}
}
