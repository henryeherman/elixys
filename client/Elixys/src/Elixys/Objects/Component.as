package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class Component extends JSONObject
	{
		// Constructor
		public function Component(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}

		// Data wrappers
		public function get Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function set Type(value:String):void
		{
			super.flash_proxy::setProperty("type", value);
		}
		
		public function get ComponentType():String
		{
			return super.flash_proxy::getProperty("componenttype");
		}
		public function set ComponentType(value:String):void
		{
			super.flash_proxy::setProperty("componenttype", value);
		}

		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get ID():uint
		{
			return parseInt(super.flash_proxy::getProperty("id"));
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}

		public function get Reactor():uint
		{
			return parseInt(super.flash_proxy::getProperty("reactor"));
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}

		public function get ReactorDescription():String
		{
			return super.flash_proxy::getProperty("reactordescription");
		}
		public function set ReactorDescription(value:String):void
		{
			super.flash_proxy::setProperty("reactordescription", value);
		}

		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}
		public function set ReactorValidation(value:String):void
		{
			super.flash_proxy::setProperty("reactorvalidation", value);
		}

		// Overridden by derived classes to format additional component details
		protected function FormatComponentDetails():String
		{
			return "";
		}

		// Convert to a JSON string
		public override function toString():String
		{
			// Give our derived class a chance to format additional details
			var sAdditionalDetails:String = FormatComponentDetails();
			
			// Create a JSON response string that will be recognized by the server
			var sJSON:String = "{";
			sJSON += JSONDataString("type", Type);
			sJSON += JSONDataString("componenttype", ComponentType);
			sJSON += JSONDataString("name", Name);
			sJSON += JSONDataInteger("id", ID);
			if (sAdditionalDetails == "")
			{
				sJSON += JSONDataInteger("reactor", Reactor, false);
			}
			else
			{
				sJSON += JSONDataInteger("reactor", Reactor);
				sJSON += sAdditionalDetails;
			}
			sJSON += "}";
			return sJSON;
		}
		
		// Type
		static public var TYPE:String = "component";
	}
}
