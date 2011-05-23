package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentReact extends Component
	{
		// Constructor
		public function ComponentReact(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Position():String
		{
			return super.flash_proxy::getProperty("position");
		}
		public function set Position(value:String):void
		{
			super.flash_proxy::setProperty("position", value);
		}
			
		public function get Duration():String
		{
			return super.flash_proxy::getProperty("duration");
		}
		public function set Duration(value:String):void
		{
			super.flash_proxy::setProperty("duration", value);
		}

		public function get DurationDescription():String
		{
			return super.flash_proxy::getProperty("durationdescription");
		}
		public function set DurationDescription(value:String):void
		{
			super.flash_proxy::setProperty("durationdescription", value);
		}

		public function get DurationValidation():String
		{
			return super.flash_proxy::getProperty("durationvalidation");
		}
		public function set DurationValidation(value:String):void
		{
			super.flash_proxy::setProperty("durationvalidation", value);
		}
	
		public function get ReactionTemperature():String
		{
			return super.flash_proxy::getProperty("reactiontemperature");
		}
		public function set ReactionTemperature(value:String):void
		{
			super.flash_proxy::setProperty("reactiontemperature", value);
		}
	
		public function get ReactionTemperatureDescription():String
		{
			return super.flash_proxy::getProperty("reactiontemperaturedescription");
		}
		public function set ReactionTemperatureDescription(value:String):void
		{
			super.flash_proxy::setProperty("reactiontemperaturedescription", value);
		}
	
		public function get ReactionTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("reactiontemperaturevalidation");
		}
		public function set ReactionTemperatureValidation(value:String):void
		{
			super.flash_proxy::setProperty("reactiontemperaturevalidation", value);
		}
	
		public function get FinalTemperature():String
		{
			return super.flash_proxy::getProperty("finaltemperature");
		}
		public function set FinalTemperature(value:String):void
		{
			super.flash_proxy::setProperty("finaltemperature", value);
		}
	
		public function get FinalTemperatureDescription():String
		{
			return super.flash_proxy::getProperty("finaltemperaturedescription");
		}
		public function set FinalTemperatureDescription(value:String):void
		{
			super.flash_proxy::setProperty("finaltemperaturedescription", value);
		}
	
		public function get FinalTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("finaltemperaturevalidation");
		}
		public function set FinalTemperatureValidation(value:String):void
		{
			super.flash_proxy::setProperty("finaltemperaturevalidation", value);
		}
	
		public function get StirSpeed():uint
		{
			return parseInt(super.flash_proxy::getProperty("stirspeed"));
		}
		public function set StirSpeed(value:uint):void
		{
			super.flash_proxy::setProperty("stirspeed", value.toString());
		}
	
		public function get StirSpeedDescription():String
		{
			return super.flash_proxy::getProperty("stirspeeddescription");
		}
		public function set StirSpeedDescription(value:String):void
		{
			super.flash_proxy::setProperty("stirspeeddescription", value);
		}
	
		public function get StirSpeedValidation():String
		{
			return super.flash_proxy::getProperty("stirespeedvalidation");
		}
		public function set StirSpeedValidation(value:String):void
		{
			super.flash_proxy::setProperty("stirespeedvalidation", value);
		}

		// Type
		static public var TYPE:String = "REACT";
	}
}