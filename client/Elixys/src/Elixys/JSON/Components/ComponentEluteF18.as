package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	import Elixys.JSON.State.Reagent;
	
	import flash.utils.flash_proxy;
	
	public class ComponentEluteF18 extends ComponentBase
	{
		// Constructor
		public function ComponentEluteF18(data:String = null, existingcontent:Object = null)
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
			return "ELUTEF18";
		}
		public static function get SKINUP():Class
		{
			return tools_elute_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_elute_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_elute_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_elute_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 4;
		public static var FIELDLABELS:Array = [
			"REACTOR", 
			"REAGENT", 
			"DURATION", 
			"PRESSURE"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT
		];
		public static var FIELDUNITS:Array = [
			"", 
			"", 
			"SECONDS", 
			"PSI"
		];
		public static var FIELDPROPERTIES:Array = [
			"Reactor", 
			"EluteReagent", 
			"EluteTime", 
			"ElutePressure"
		];
		
		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}
		
		public function get EluteTime():uint
		{
			return super.flash_proxy::getProperty("elutetime");
		}
		public function set EluteTime(value:uint):void
		{
			super.flash_proxy::setProperty("elutetime", value);
		}
		
		public function get EluteTimeValidation():String
		{
			return super.flash_proxy::getProperty("elutetimevalidation");
		}
		
		public function get ElutePressure():uint
		{
			return super.flash_proxy::getProperty("elutepressure");
		}
		public function set ElutePressure(value:uint):void
		{
			super.flash_proxy::setProperty("elutepressure", value);
		}
		
		public function get ElutePressureValidation():String
		{
			return super.flash_proxy::getProperty("elutepressurevalidation");
		}

		public function get EluteReagent():Reagent
		{
			if (m_pReagent == null)
			{
				m_pReagent = new Reagent(null, super.flash_proxy::getProperty("reagent"));
			}
			return m_pReagent;
		}
		public function set EluteReagent(value:Reagent):void
		{
			super.flash_proxy::setProperty("reagent", value);
			m_pReagent = null;
		}
		
		public function get EluteReagentValidation():String
		{
			return super.flash_proxy::getProperty("reagentvalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sEluteF18Details:String = JSONDataObject("reactor", Reactor);
			sEluteF18Details += JSONDataObject("elutetime", EluteTime);
			sEluteF18Details += JSONDataObject("elutepressure", ElutePressure);
			sEluteF18Details += JSONDataObject("reagent", EluteReagent.ReagentID, false);
			return sEluteF18Details;
		}

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentEluteF18A:ComponentEluteF18 = new ComponentEluteF18(null, pComponentA);
			var pComponentEluteF18B:ComponentEluteF18 = new ComponentEluteF18(null, pComponentB);
			if (pComponentEluteF18A.Reactor != pComponentEluteF18B.Reactor)
			{
				return false;
			}
			if (pComponentEluteF18A.EluteTime != pComponentEluteF18B.EluteTime)
			{
				return false;
			}
			if (pComponentEluteF18A.ElutePressure != pComponentEluteF18B.ElutePressure)
			{
				return false;
			}
			if (!Reagent.CompareReagents(pComponentEluteF18A.EluteReagent, pComponentEluteF18B.EluteReagent))
			{
				return false;
			}
			if (pComponentEluteF18A.EluteReagentValidation != pComponentEluteF18B.EluteReagentValidation)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sReactorError = ValidateField(Reactor, ReactorValidation);
			m_sEluteTimeError = ValidateField(EluteTime, EluteTimeValidation);
			m_sElutePressureError = ValidateField(ElutePressure, ElutePressureValidation);
			m_sEluteReagentError = ValidateField(EluteReagent, EluteReagentError);
		}
		
		// Validation fields
		public function get ReactorError():String
		{
			return m_sReactorError;
		}
		public function get EluteTimeError():String
		{
			return m_sEluteTimeError;
		}
		public function get ElutePressureError():String
		{
			return m_sElutePressureError;
		}
		public function get EluteReagentError():String
		{
			return m_sEluteReagentError;
		}
		
		// State components
		private var m_pReagent:Reagent;

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"ELUTEF18\"," +
			"\"id\":0," +
			"\"note\":\"\"," +
			"\"reactor\":0," +
			"\"elutetime\":0," +
			"\"elutepressure\":0," +
			"\"reagent\":" + Reagent.DEFAULT + "}";
		
		// Validation errors
		protected var m_sReactorError:String = "";
		protected var m_sEluteTimeError:String = "";
		protected var m_sElutePressureError:String = "";
		protected var m_sEluteReagentError:String = "";
	}
}
