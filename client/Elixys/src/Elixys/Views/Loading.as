package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.Components.*;
	import Elixys.Events.*;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.TimerEvent;
	import flash.utils.Timer;	

	// This loading view is an extension of our extended Form class
	public class Loading extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Loading(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			var pXML:XML;
			if (!Styling.bSmallScreenDevice)
			{
				pXML = LOADING_FULLSCREEN;
			}
			else
			{
				pXML = LOADING_SMALLSCREEN;
			}
			super(screen, pXML, attributes, row, inGroup);
		}
		
		/***
		 * Member functions
		 **/
		
		// Called when this view is first displayed
		public function InitialDisplay():void
		{
			// Get references to the logo and progress
			m_pLogo = Logo(findViewById("Logo"));
			m_pProgressBar = ProgressBar(findViewById("Progress"));

			// Fade in the logo component
			m_pLogo.Fade(0, 1, 600);

			// Set a timer to delay the fading in of the progress component
			m_pProgressDelayTimer = new Timer(450, 1);
			m_pProgressDelayTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnProgressDelayTimerComplete);
			m_pProgressDelayTimer.start();
		}

		// Called when the progress delay timer completes
		protected function OnProgressDelayTimerComplete(event:TimerEvent):void
		{
			// Remove the event listener
			m_pProgressDelayTimer.removeEventListener(TimerEvent.TIMER_COMPLETE, OnProgressDelayTimerComplete);
			
			// Fade in the progress component
			m_pProgressBar.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeInComplete);
			m_pProgressBar.Fade(0, 1, 500);
		}

		// Called when the progress fade in transition is complete
		protected function OnProgressFadeInComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pProgressBar.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeInComplete);
			
			// Dispatch a transition complete event
			dispatchEvent(new TransitionCompleteEvent(this));
		}

		// Sets the percent complete
		public function SetProgress(fPercentComplete:Number):void
		{
			m_pProgressBar.SetProgress(fPercentComplete);	
		}

		// Called when the load is complete
		public function LoadComplete():void
		{
			// Fade out the progress component
			m_pProgressBar.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeOutComplete);
			m_pProgressBar.Fade(1, 0, 300);
		}
		
		// Called when the progress fade out transition is complete
		protected function OnProgressFadeOutComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pProgressBar.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeOutComplete);

			// Dispatch a transition complete event
			dispatchEvent(new TransitionCompleteEvent(this));
		}

		/***
		 * Member variables
		 **/


		// Loading view XML
		protected static const LOADING_FULLSCREEN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND}>
				<rows gapV="0" border="false" heights="18%,64%,9%,9%" background={Styling.APPLICATION_BACKGROUND}>
					<frame />
					<columns gapH="0" widths="34%,66%">
						<logo id="Logo" visible="false" />
						<frame />
					</columns>
					<frame />
					<progressbar id="Progress" />
				</rows>
			</frame>;
		protected static const LOADING_SMALLSCREEN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND}>
				<rows gapV="0" border="false" heights="40%,38%,20%" background={Styling.APPLICATION_BACKGROUND}>
					<logo id="Logo" visible="false" />
					<frame />
					<progressbar id="Progress" />
				</rows>
			</frame>;

		// References to components
		protected var m_pLogo:Logo;
		protected var m_pProgressBar:ProgressBar;
		
		// Progress delay timer
		protected var m_pProgressDelayTimer:Timer;
	}
}

