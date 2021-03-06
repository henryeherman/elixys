package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentComment extends ComponentBase
	{
		// Constructor
		public function ComponentComment(data:String = null, existingcontent:Object = null)
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
			return "COMMENT";
		}
		public static function get SKINUP():Class
		{
			return tools_comment_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_comment_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_comment_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_comment_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 2;
		public static var FIELDLABELS:Array = [
			"COMMENT",
			"BROADCAST"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_MULTILINEINPUT,
			Constants.TYPE_CHECKBOX
		];
		public static var FIELDUNITS:Array = [
			"",
			""
		];
		public static var FIELDPROPERTIES:Array = [
			"Comment",
			"BroadcastFlag"
		];

		// Data wrappers
		public function get Comment():String
		{
			return unescape(super.flash_proxy::getProperty("comment"));
		}
		public function set Comment(value:String):void
		{
			super.flash_proxy::setProperty("comment", escape(value));
		}
		
		public function get CommentValidation():String
		{
			return super.flash_proxy::getProperty("commentvalidation");
		}

		public function get BroadcastFlag():uint
		{
			return super.flash_proxy::getProperty("broadcastflag");
		}
		public function set BroadcastFlag(value:uint):void
		{
			super.flash_proxy::setProperty("broadcastflag", value);
		}
		
		public function get BroadcastFlagValidation():String
		{
			return super.flash_proxy::getProperty("broadcastflagvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sComponentDetails:String = JSONDataString("comment", escape(Comment));
			sComponentDetails += JSONDataObject("broadcastflag", BroadcastFlag, false);
			return sComponentDetails;
		}
		
		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentCommentA:ComponentComment = new ComponentComment(null, pComponentA);
			var pComponentCommentB:ComponentComment = new ComponentComment(null, pComponentB);
			if (pComponentCommentA.Comment != pComponentCommentB.Comment)
			{
				return false;
			}
			if (pComponentCommentA.BroadcastFlag != pComponentCommentB.BroadcastFlag)
			{
				return false;
			}
			return true;
		}

		// Validates the comment component
		public override function Validate():void
		{
			m_sCommentError = ValidateField(Comment, CommentValidation);
			m_sBroadcastFlagError = ValidateField(BroadcastFlag, BroadcastFlagValidation);
		}
		
		// Validation fields
		public function get CommentError():String
		{
			return m_sCommentError;
		}
		public function get BroadcastFlagError():String
		{
			return m_sBroadcastFlagError;
		}

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"COMMENT\"," +
			"\"id\":0," +
			"\"note\":\"\"," +
			"\"comment\":\"\"," +
			"\"broadcastflag\":0}";
		
		// Validation errors
		protected var m_sCommentError:String = "";
		protected var m_sBroadcastFlagError:String = "";
	}
}
