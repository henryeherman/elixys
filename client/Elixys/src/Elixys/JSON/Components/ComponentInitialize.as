package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentInitialize extends ComponentBase
	{
		// Constructor
		public function ComponentInitialize(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "INITIALIZE";
		}
		public static function get SKINUP():Class
		{
			return tools_initialize_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_initialize_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_initialize_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_initialize_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 0;
		public static var FIELDLABELS:Array = [];
		public static var FIELDTYPES:Array = [];
		public static var FIELDUNITS:Array = [];
		public static var FIELDPROPERTIES:Array = [];
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return "";
		}
		
		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			return true;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"INITIALIZE\"," +
			"\"id\":0," +
			"\"note\":\"\"}";
	}
}
