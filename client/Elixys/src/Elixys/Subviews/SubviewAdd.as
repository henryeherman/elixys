package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentAdd;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This add subview is an extension of the unit operation subview class
	public class SubviewAdd extends SubviewUnitOperation
	{
		public function SubviewAdd(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentAdd.COMPONENTTYPE, attributes);
		}
	}
}