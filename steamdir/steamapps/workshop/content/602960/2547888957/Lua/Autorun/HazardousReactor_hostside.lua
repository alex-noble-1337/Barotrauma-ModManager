if Game.IsMultiplayer and CLIENT then return end

local geigerRadsIndex = {}

Hook.Add("geigercount", "geigereffect", function (effect, deltaTime, item, targets, worldPosition)
  if targets[1] == nil then item.condition = 100 return end
  if geigerRadsIndex[item] == nil then geigerRadsIndex[item] = 0 end

  local c = targets[1]
  local r = c.CharacterHealth.GetAffliction("radiationgeiger")
  local rads = 0
  if(r) then
    rads = r.Strength
  end

  local deltaRads = math.max(rads - geigerRadsIndex[item], 0)
  item.condition = 100 - (deltaRads * 10)
  geigerRadsIndex[item] = rads

end)

--To Swap out Inactive for Active Fuelrod
Hook.Add("fuelrodswap", "rodswap", function (effect, deltaTime, item, targets, worldPosition)
  if targets[1] == nil then return end
  local old_rod = targets[1]
  local old_rod_identifier = old_rod.Prefab.Identifier.Value
  local old_rod_conidition = old_rod.Condition
  local old_rod_quality = old_rod.Quality

  Entity.Spawner.AddEntityToRemoveQueue(old_rod)

  Timer.Wait(function() 
    local prefab = ItemPrefab.GetItemPrefab(old_rod_identifier.."_active")
    Entity.Spawner.AddItemToSpawnQueue(prefab, item.ownInventory, old_rod_conidition, old_rod_quality)
  end,
  100)

end)


--update/sync reactor!
LuaUserData.MakeFieldAccessible(Descriptors["Barotrauma.Items.Components.Reactor"], "unsentChanges")

--Fulgurium Fuel rod Special effect AutoReactor Control
Hook.Add("fulguriumrodspecial", "fulguriumrodspecialed", function (effect, deltaTime, item, targets, worldPosition)
  if targets[1] == nil then return end
  local fuelrod = targets[1]
  local lightcomp = fuelrod.GetComponentString("LightComponent")

  if lightcomp.Range > 0 then
    local reactor = item.GetComponentString("Reactor")
    local correctionvalue = reactor.CorrectTurbineOutput - reactor.TargetTurbineOutput
    if math.abs(correctionvalue) < 15 then return end
    --Host Only!
    if correctionvalue > 0 then
      reactor.TargetTurbineOutput = reactor.TargetTurbineOutput + 5
    else
      reactor.TargetTurbineOutput = reactor.TargetTurbineOutput - 5
    end
    fuelrod.Condition = fuelrod.Condition - 15
    reactor.unsentChanges = true

  end
end)


local heatspikeprefab = ItemPrefab.GetItemPrefab("heatspikeemitter")

--Incendium Fuel rod Special effect, Uncontrolled Reactor Temp! + Spawning "heat spikes"  
Hook.Add("incendiumrodspecial", "incendiumrodspecialed", function (effect, deltaTime, item, targets, worldPosition)
  if targets[1] == nil then return end
  local fuelrod = targets[1]
  local lightcomp = fuelrod.GetComponentString("LightComponent")
  local reactor = item.GetComponentString("Reactor")
  local luckynumber = math.random(1000)
--Higher the number, the worse it is!

  if lightcomp.Range < 300 then
    if luckynumber > 950 then
      reactor.Temperature = reactor.Temperature + 30
      reactor.unsentChanges = true
      fuelrod.Condition = fuelrod.Condition - 1
    elseif luckynumber > 700 then
      reactor.Temperature = reactor.Temperature + 20
      reactor.unsentChanges = true
      fuelrod.Condition = fuelrod.Condition - 0.5
    end
  elseif lightcomp.Range < 450 then
    if luckynumber > 995 then
      Entity.Spawner.AddItemToSpawnQueue(heatspikeprefab, fuelrod.ownInventory,nil,nil,nil,false)
      fuelrod.Condition = fuelrod.Condition - 5
    elseif luckynumber > 900 then
      reactor.Temperature = reactor.Temperature + 30
      reactor.unsentChanges = true
      fuelrod.Condition = fuelrod.Condition - 1
    elseif luckynumber > 700 then
      reactor.Temperature = reactor.Temperature + 20
      reactor.unsentChanges = true
      fuelrod.Condition = fuelrod.Condition - 0.5
    end
  else
    if luckynumber > 950 then
      Entity.Spawner.AddItemToSpawnQueue(heatspikeprefab, fuelrod.ownInventory,nil,nil,nil,false)
      fuelrod.Condition = fuelrod.Condition - 5
    elseif luckynumber > 800 then
      reactor.Temperature = reactor.Temperature + 30
      reactor.unsentChanges = true
      fuelrod.Condition = fuelrod.Condition - 1
    elseif luckynumber > 400 then
      reactor.Temperature = reactor.Temperature + 20
      reactor.unsentChanges = true
      fuelrod.Condition = fuelrod.Condition - 0.5
    end
  end
end)