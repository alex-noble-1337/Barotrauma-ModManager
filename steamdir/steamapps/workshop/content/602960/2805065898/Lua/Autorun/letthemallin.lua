LuaUserData.RegisterType("Barotrauma.RagdollParams") -- todo remove next lua update
LuaUserData.RegisterType("Barotrauma.CharacterParams") -- todo remove next lua update
local desc = LuaUserData.RegisterType("Barotrauma.CharacterParams+AIParams") -- todo remove next lua update

LuaUserData.MakeMethodAccessible(desc, "set_AggressiveBoarding")

Hook.Add("characterCreated", "get better", function(character)
   character.AnimController.RagdollParams.CanEnterSubmarine = true

   if LuaUserData.IsTargetType(character.AIController, "Barotrauma.EnemyAIController") then
      character.AIController.AIParams.set_AggressiveBoarding(true)
   end
end)