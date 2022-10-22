--Reactor repair speed override
Hook.Add("roundStart", "changeRepairThingyOfReactors", function()
  for k, v in pairs(Item.ItemList) do
     local repairable = v.GetComponentString("Repairable")
     if repairable and v.Submarine == Submarine.MainSub and  v.GetComponentString("Reactor") then
        repairable.RepairThreshold = 80
        repairable.MinDeteriorationCondition = 0
    repairable.FixDurationLowSkill = 60
    repairable.FixDurationHighSkill = 30
    repairable.MinDeteriorationDelay = 120
    repairable.MinDeteriorationDelay = 240
    
     end
  end
end)

--Rod Hazard LightComponent Force Update when Broken
Hook.Patch(
"Barotrauma.Items.Components.LightComponent",
"UpdateBroken", 
function (instance, ptable)
-- Only force update if reactorfuel tag is here
  if instance.item.HasTag("reactorfuel") then
    ptable.PreventExecution = true
    local lightcomp = instance.item.GetComponentString("LightComponent")
    lightcomp.Update(ptable["deltaTime"],ptable["cam"])
  end
  return nil
end, Hook.HookMethodType.Before)


--Fuel Out for Fulgurium Fuel rod
Hook.Add("fulguriumavailablefuel", "fulguriumfuel", function (effect, deltaTime, item, targets, worldPosition)
  if targets[1] == nil then return end
  local fuelrod = targets[1]
  local lc = fuelrod.GetComponentString("LightComponent")

  if lc.Range > 0 then
    local reactor = item.GetComponentString("Reactor")
    reactor.AvailableFuel = reactor.AvailableFuel + 40.0
  end
end)

--Fuel Out for Fulgurium Fuel rod
Hook.Add("incendiumavailablefuel", "incendiumfuel", function (effect, deltaTime, item, targets, worldPosition)
  if targets[1] == nil then return end
  local fuelrod = targets[1]
  local lc = fuelrod.GetComponentString("LightComponent")
  local reactor = item.GetComponentString("Reactor")



  if lc.Range < 300 then
    reactor.AvailableFuel = reactor.AvailableFuel + 180.0
  elseif lc.Range < 450 then
    reactor.AvailableFuel = reactor.AvailableFuel + 320.0
  else
    reactor.AvailableFuel = reactor.AvailableFuel + 570.0
  end
end)