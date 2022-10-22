local SRC_NAMESPACE       = "com.github.cintique.ConsentRequired."
local MAIN                = "Main"
local LUA_EVENT_LOADED    = "loaded"
local HOOK_NAME_ON_LOADED = "com.github.cintique.ConsentRequired.onLoaded"

local function onLoaded()
  -- Only run client side if not multiplayer
  ---@diagnostic disable-next-line: undefined-global
  if Game.IsMultiplayer and CLIENT then return end

  local requireStr = SRC_NAMESPACE .. MAIN

  require(requireStr)
end

Hook.Add(
  LUA_EVENT_LOADED,
  HOOK_NAME_ON_LOADED,
  onLoaded
)
