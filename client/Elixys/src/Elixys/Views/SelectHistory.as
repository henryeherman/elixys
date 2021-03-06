package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.Components.*;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Post.PostSelect;
	import Elixys.JSON.State.*;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This select history view is an extension of the Screen class
	public class SelectHistory extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function SelectHistory(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, SELECTHISTORY, attributes, row, inGroup);
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			// This view isn't used on small screen devices
			if (Styling.bSmallScreenDevice)
			{
				return false;
			}

			if (m_nChildrenLoaded < LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar();
				}
				
				// Step 2 is loading the tab bar
				if (m_nChildrenLoaded == 1)
				{
					LoadTabBar();
				}
				
				// Step 3 is loading the sequence grid
				if (m_nChildrenLoaded == 2)
				{
					LoadDataGrid();
				}
				
				// Increment and return
				++m_nChildrenLoaded;
				return true;
			}
			else
			{
				// Load complete
				return false;
			}
		}

		// Load the navigation bar
		protected function LoadNavigationBar():void
		{
			// Get the navigation bar container
			var pContainer:Form = Form(findViewById("selecthistory_navigationbar_container"));
			
			// Load the navigation bar
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pNavigationBar = new NavigationBar(pContainer, NAVIGATION, pAttributes);
			m_pNavigationBar.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			
			// Append the navigation bar to the XML and refresh
			pContainer.xml.appendChild(NAVIGATION);
			pContainer.AppendChild(m_pNavigationBar);
			layout(attributes);
		}

		// Load the tab bar
		protected function LoadTabBar():void
		{
			// Get the tab bar container
			var pContainer:Form = Form(findViewById("selecthistory_tabbar_container"));
			
			// Load the tab bar
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pTabBar = new TabBar(pContainer, TAB, pAttributes);
			m_pTabBar.addEventListener(ButtonEvent.CLICK, OnTabClick);
			
			// Append the tab bar to the XML and refresh
			pContainer.xml.appendChild(TAB);
			pContainer.AppendChild(m_pTabBar);
			layout(attributes);
		}

		// Load the data grid
		protected function LoadDataGrid():void
		{
			// Get the data grid container
			var pContainer:Form = Form(findViewById("selecthistory_datagrid_container"));
			
			// Load the datagrid
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			m_pDataGrid = new DataGrid(pContainer, DATAGRID, pAttributes);
			m_pDataGrid.addEventListener(ButtonEvent.CLICK, OnHeaderClick);
			m_pDataGrid.addEventListener(SelectionEvent.CHANGE, OnSelectionChange);

			// Append the data grid to the XML and refresh
			pContainer.xml.appendChild(DATAGRID);
			pContainer.AppendChild(m_pDataGrid);
			layout(attributes);
		}

		/***
		 * Member functions
		 **/
		
		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Check what has changed since our last update
			var pStateSelect:StateSelect = new StateSelect(null, pState);
			var bButtonsChanged:Boolean = true, bTabsChanged:Boolean = true, bTabIDChanged:Boolean = true, bColumnsChanged:Boolean = true,
				bSequencesChanged:Boolean = true;
			if (m_pStateSelect != null)
			{
				bButtonsChanged = !Elixys.JSON.State.Button.CompareButtonArrays(pStateSelect.Buttons, m_pStateSelect.Buttons);
				bTabsChanged = !Tab.CompareTabArrays(pStateSelect.Tabs, m_pStateSelect.Tabs);
				bTabIDChanged = (pStateSelect.TabID != m_pStateSelect.TabID);
				bColumnsChanged = !Column.CompareColumnArrays(pStateSelect.Columns, m_pStateSelect.Columns);
				bSequencesChanged = !SequenceMetadata.CompareSequenceMetadataArrays(pStateSelect.Sequences, m_pStateSelect.Sequences);
			}
			
			// Update the navigation bar buttons
			if (bButtonsChanged)
			{
				m_pNavigationBar.UpdateButtons(pStateSelect.Buttons);
			}
			
			// Update the tab bar options
			if (bTabsChanged || bTabIDChanged)
			{
				m_pTabBar.UpdateTabs(pStateSelect.Tabs, pStateSelect.TabID);
			}
			
			// Update the data grid
			if (bTabsChanged || bTabIDChanged || bColumnsChanged || bSequencesChanged)
			{
				// Update the grid
				m_pDataGrid.UpdateDataGrid(pStateSelect.Columns, pStateSelect.Sequences);
			}
			
			// Remember the last state
			m_pStateSelect = pStateSelect;
		}
		
		// Called when a button on the navigation bar is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			// Send a button click to the server
			var pPostSelect:PostSelect = new PostSelect();
			pPostSelect.Type = "BUTTONCLICK";
			pPostSelect.TargetID = event.button;
			pPostSelect.SequenceID = m_pDataGrid.SelectionID;
			DoPost(pPostSelect, "SELECT");
		}
		
		// Called when a tab on the tab bar is clicked
		protected function OnTabClick(event:ButtonEvent):void
		{
			// Send a tab click to the server
			var pPostSelect:PostSelect = new PostSelect();
			pPostSelect.Type = "TABCLICK";
			pPostSelect.TargetID = event.button;
			DoPost(pPostSelect, "SELECT");
		}
		
		// Called when a header on data grid is clicked
		protected function OnHeaderClick(event:ButtonEvent):void
		{
			// Send a header click to the server
			var pPostSelect:PostSelect = new PostSelect();
			pPostSelect.Type = "HEADERCLICK";
			pPostSelect.TargetID = event.button;
			DoPost(pPostSelect, "SELECT");
		}

		// Called when the grid selection changes
		protected function OnSelectionChange(event:SelectionEvent):void
		{
			// Pass the selection to the navigation bar
			m_pNavigationBar.UpdateSelection(event.selectionID);
		}
		
		/***
		 * Member variables
		 **/

		// Select saved screen XML
		protected static const SELECTHISTORY:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,2%,7%,73%" alignH="fill" alignV="fill">
					<frame id="selecthistory_navigationbar_container" alignV="fill" alignH="fill" />
					<frame alignV="fill" alignH="fill" />
					<frame id="selecthistory_tabbar_container" alignV="fill" alignH="fill" />
					<frame id="selecthistory_datagrid_container" alignV="fill" alignH="fill" />
				</rows>
			</frame>;

		// Navigation bar XML
		protected static const NAVIGATION:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(blueNavigationBar_mc)} rightpadding="20">
				<navigationbaroption name="SEQUENCER" backgroundskinheightpercent="72" foregroundskinheightpercent="30"
						fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY1}
						backgroundskinup={getQualifiedClassName(mainNav_activeBtnOutline_up)}
						backgroundskindown={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						backgroundskindisabled={getQualifiedClassName(mainNav_activeBtnOutline_up)}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_active)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="COPYSEQUENCE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_copySequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_copySequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_copySequence_disabled)}>
					COPY SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="VIEWSEQUENCE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_viewSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_viewSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_viewSequence_disabled)}>
					VIEW SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="VIEWRUNLOGS" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_viewRunLogs_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_viewRunLogs_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_viewRunLogs_disabled)}>
					RUN LOGS
				</navigationbaroption>
				<navigationbaroption name="VIEWBATCHRECORD" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_viewBatchRecord_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_viewBatchRecord_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_viewBatchRecord_disabled)}>
					BATCH RECORD
				</navigationbaroption>
				<navigationbaroption blank="true" />
			</navigationbar>;
				
		// Tab bar XML
		protected static const TAB:XML =
			<tab alignH="fill" alignV="fill" fontFace="GothamMedium" fontSize="18" textColor={Styling.TEXT_GRAY4}
				selectedTextColor={Styling.TEXT_GRAY1} taboffset="15" textpaddingvertical="7" textpaddinghorizontal="18"/>;
		
		// Data grid XML
		protected static const DATAGRID:XML =
			<datagrid alignH="fill" alignV="fill" headerfontface="GothamMedium" headerfontsize="14" 
				headertextcolor={Styling.TEXT_GRAY5} headerpressedcolor={Styling.DATAGRID_HEADERPRESSED}
				sortupskin={getQualifiedClassName(sortUp_up)} sortdownskin={getQualifiedClassName(sortDown_up)}
				bodyfontface="GothamMedium" bodyfontsize="18" bodytextcolor={Styling.TEXT_GRAY1}
				bodytextselectedcolor={Styling.TEXT_WHITE} visiblerowcount="9" 
				rowselectedcolor={Styling.DATAGRID_SELECTED} idfield="id" />;
		
		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 3;
		
		// The current step
		protected var m_nChildrenLoaded:uint = 0;
		
		// Currently displayed state
		protected var m_pStateSelect:StateSelect;

		// Screen components
		protected var m_pNavigationBar:NavigationBar;
		protected var m_pTabBar:TabBar;
		protected var m_pDataGrid:DataGrid;
	}
}
