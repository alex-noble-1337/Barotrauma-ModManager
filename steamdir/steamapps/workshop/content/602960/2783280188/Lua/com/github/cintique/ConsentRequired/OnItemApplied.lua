local Api = require "com.github.cintique.ConsentRequired.Api"
local Barotrauma = require "com.github.cintique.ConsentRequired.Util.Barotrauma"

local ADD_ATTACKER_DAMAGE = 10

---@param aiChar Barotrauma_Character The AI character to be made hostile.
---@param instigator Barotrauma_Character The character to be the target of the AI's wrath.
local function makeHostile(aiChar, instigator)
  local attackResult = Barotrauma.AttackResult.NewAttackResultFromDamage(ADD_ATTACKER_DAMAGE)
  aiChar.OnAttacked
        .Invoke(
          instigator,
          attackResult
        )
end

---@param char1 Barotrauma_Character Character one.
---@param char2 Barotrauma_Character Character two.
---@return boolean charactersAreOnSameTeam True if characters one & two are on the same team, false otherwise.
local function isOnSameTeam(char1, char2)
  local team1 = char1.TeamID
  local team2 = char2.TeamID
  return team1 == team2
end

---@param user Barotrauma_Character The character who desires consent.
---@param target Barotrauma_Character The character who gives consent
---@return boolean consent True if consent is given, false otherwise.
local function hasConsent(user, target)
  return isOnSameTeam(user, target)
end

---@param aiChar Barotrauma_Character The (AI but not necessarily) character whose sight is being tested.
---@param target Barotrauma_Character The character to be seen.
---@return boolean aiCanSeeTarget True if the AI can see the target character.
local function canAiSeeTarget(aiChar, target)
  -- I'll just use what Barotrauma uses for witness line of sight
  local aiVisibleHulls = aiChar.GetVisibleHulls()
  local targetCurrentHull = target.CurrentHull
  for _, visibleHull in pairs(aiVisibleHulls) do
    if targetCurrentHull == visibleHull then
      return true
    end
  end
  return false
end

---@param user Barotrauma_Character The character of the instigator being witnessed.
---@param victim Barotrauma_Character The character of the victim of the crime being witnessed.
---@return Barotrauma_Character[] Characters that have witnessed the crime.
local function getWitnessesToCrime(user, victim)
  local witnesses = {}
  for _, char in pairs(Character.CharacterList) do
    if
      not char.Removed
      and not char.IsUnconscious
      and char.IsBot
      and char.IsHuman
      and isOnSameTeam(char, victim)
    then
      local isWitnessingUser = canAiSeeTarget(char, user)
      if isWitnessingUser then
        table.insert(
          witnesses,
          char
        )
      end
    end
  end
  return witnesses
end

---@param user Barotrauma_Character The character that is applying the affected item.
---@param target Barotrauma_Character The character of the target of the affected item's application.
local function onAffectedItemApplied(user, target)
  if
    not hasConsent(user, target)
    and target.IsBot
    and target.IsHuman
  then
    if
      not target.IsIncapacitated
      and target.Stun <= 1
    then
      makeHostile(target, user)
    else
      -- Vanilla Barotrauma Human AI doesn't care what you do to their unconscious teammates, even shooting them in the head
      -- Let's fix that for this particular case of mistreatment
      local witnesses = getWitnessesToCrime(user, target)
      for _, witness in pairs(witnesses) do
        makeHostile(witness, user)
      end
    end
  end
end

local function isItemAffected(identifier)
  return Api.IsItemAffected(identifier)
end

---@param item Barotrauma_Item Item being applied.
---@param user Barotrauma_Character The character that is applying the item.
---@param target Barotrauma_Character The character of the target of the item's application.
local function OnItemApplied(item, user, target)
  local itemIdentifier = item.Prefab.Identifier.Value

  if isItemAffected(itemIdentifier) then
    onAffectedItemApplied(user, target)
  end
end

return OnItemApplied
