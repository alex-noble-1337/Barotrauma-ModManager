-- Consent Required API
-- Any Lua script can access this API by adding this line:
-- local Api = require "com.github.cintique.ConsentRequired.Api"

local Environment = require 'com.github.cintique.ConsentRequired.Util.Environment'

local _ENV = Environment.PrepareEnvironment(_ENV)

-- Table of identifiers (strings) of items that when used
-- as a treatment on an NPC from a different team,
-- causes that NPC (and their allies) to become hostile
-- towards the player.
local affectedItems = {}

---Adds an item (by identifier string) to `affectedItems`.
---@param identifier string
function AddAffectedItem(identifier)
	table.insert(
		affectedItems,
		identifier
	)
end

---Returns a boolean indicating whether a given item is affected or not.
---@param identifier string The identifier of the item that we are testing.
---@return boolean isAffected True if the item is affected, false otherwise.
function IsItemAffected(identifier)
	for _, item in pairs(affectedItems) do
		if item == identifier then
			return true
		end
	end
	return false
end

return Environment.Export(_ENV)
