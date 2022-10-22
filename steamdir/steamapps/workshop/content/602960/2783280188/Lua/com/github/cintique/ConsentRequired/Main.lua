-- Do not take my blood or organs without my consent, thanks.
-- Causes AI to get angry at you if you use certain medical items on them.
-- These items are those related to organ and blood removal.
-- This mod is meant to be accompanied by Neurotrauma, and aims to
-- resolve the issue of being freely able to steal blood/organs from
-- neutral NPCs (e.g. outposts, VIPs) without them getting mad at you.

local Api           = require "com.github.cintique.ConsentRequired.Api"
local OnItemApplied = require "com.github.cintique.ConsentRequired.OnItemApplied"
local Config        = require "com.github.cintique.ConsentRequired.Config"

local LUA_EVENT_ITEM_APPLYTREATMENT = "item.ApplyTreatment"
local HOOK_NAME_ITEM_APPLYTREATMENT = "com.github.cintique.ConsentRequired.onItemApplyTreatment"

-- Set up affected items from config.
for _, affectedItem in pairs(Config.AffectedItems) do
  Api.AddAffectedItem(affectedItem)
end

Hook.Add(
  LUA_EVENT_ITEM_APPLYTREATMENT,
  HOOK_NAME_ITEM_APPLYTREATMENT,
  OnItemApplied
)
