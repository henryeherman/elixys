package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentInstall extends Component
	{
		// Constructor
		public function ComponentInstall(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = m_sDefault;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Message():String
		{
			return super.flash_proxy::getProperty("message");
		}
		public function set Message(value:String):void
		{
			super.flash_proxy::setProperty("message", value);
		}
		
		public function get MessageDescription():String
		{
			return super.flash_proxy::getProperty("messagedescription");
		}
		public function set MessageDescription(value:String):void
		{
			super.flash_proxy::setProperty("messagedescription", value);
		}
		
		public function get MessageValidation():String
		{
			return super.flash_proxy::getProperty("messagevalidation");
		}
		public function set MessageValidation(value:String):void
		{
			super.flash_proxy::setProperty("messagevalidation", value);
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataString("message", Message, false);
		}

		// Type
		static public var TYPE:String = "INSTALL";

		// Default format
		private var m_sDefault:String = "{ \"type\":\"component\", \"componenttype\":\"INSTALL\", \"name\":\"\", \"componentid\":\"\", " +
			"\"sequenceid\":\"\", \"reactor\":\"\", \"reactordescription\":\"\", \"reactorvalidation\":\"\", \"message\":\"\", " +
			"\"messagedescription\":\"\", \"messagevalidation\":\"\" }";
	}
}
