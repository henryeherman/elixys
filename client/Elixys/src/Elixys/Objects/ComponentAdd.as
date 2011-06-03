package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentAdd extends Component
	{
		// Constructor
		public function ComponentAdd(data:String = null, existingcontent:Object = null)
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
		public function get Reagent():uint
		{
			return parseInt(super.flash_proxy::getProperty("reagent"));
		}
		public function set Reagent(value:uint):void
		{
			super.flash_proxy::setProperty("reagent", value);
		}
		
		public function get ReagentDescription():String
		{
			return super.flash_proxy::getProperty("reagentdescription");
		}
		public function set ReagentDescription(value:String):void
		{
			super.flash_proxy::setProperty("reagentdescription", value);
		}

		public function get ReagentValidation():String
		{
			return super.flash_proxy::getProperty("reagentvalidation");
		}
		public function set ReagentValidation(value:String):void
		{
			super.flash_proxy::setProperty("reagentvalidation", value);
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return JSONDataInteger("reagent", Reagent, false);
		}

		// Type
		static public var TYPE:String = "ADD";
	}
}
