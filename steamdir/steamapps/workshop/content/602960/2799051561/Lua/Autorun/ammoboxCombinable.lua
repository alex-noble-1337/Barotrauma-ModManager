Hook.Add("item.created", "changeAmmoBoxitemcreated", function(item)
   if item.HasTag("ammobox") or item.HasTag("coilgunammo") then
		local holdable = item.GetComponentString("Holdable")
		if holdable.CanBeCombined == false or holdable.RemoveOnCombined == true then
			holdable.CanBeCombined = true
			holdable.RemoveOnCombined = false
		end
	end
end)