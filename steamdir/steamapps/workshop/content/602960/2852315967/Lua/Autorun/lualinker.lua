local function FindClosestItem(submarine, position)
    local closest = nil
    for key, value in pairs(submarine and submarine.GetItems(false) or Item.ItemList) do
        if value.HasTag("container") or value.HasTag("fabricator") or value.HasTag("deconstructor") or value.HasTag("turret") or value.HasTag("turretammosource") or value.HasTag("lualinkable") or value.HasTag("oxygengenerator") or value.HasTag("vent") then
            if Vector2.Distance(position, value.WorldPosition) < 100 then
                if closest == nil then closest = value end

                if Vector2.Distance(position, value.WorldPosition) < Vector2.Distance(position, closest.WorldPosition) then
                    closest = value
                end
            end
        end
    end
    return closest
end

local function FindClientCharacter(character)
    if CLIENT then return nil end
    
    for key, value in pairs(Client.ClientList) do
        if value.Character == character then
            return value
        end
    end
end

local function AddMessage(text, client)
    local message = ChatMessage.Create("Lua Linker", text, ChatMessageType.Default, nil, nil)
    message.Color = Color(60, 100, 255)

    if CLIENT then
        Game.ChatBox.AddMessage(message)
    else
        Game.SendDirectChatMessage(message, client)
    end
end

local links = {}

Hook.Add("luaLinker.onUse", "examples.luaLinker", function(statusEffect, delta, item)
    if CLIENT and Game.IsMultiplayer then return end -- server side only in multiplayer, client side in singleplayer

    if item.ParentInventory == nil or item.ParentInventory.Owner == nil then return end

    local owner = FindClientCharacter(item.ParentInventory.Owner)

    local target = FindClosestItem(item.Submarine, item.WorldPosition)

    if target == nil then
        AddMessage("No item found", owner)
        return
    end

    if links[item] == nil then
        links[item] = target
        AddMessage(string.format("Link Start: \"%s\"", target.Name), owner)
    else
        local otherTarget = links[item]

        if otherTarget == target then
            AddMessage("The linked items cannot be the same", owner)
            links[item] = nil
            return
        end

        for key, value in pairs(target.linkedTo) do
            if value == otherTarget then
                target.RemoveLinked(otherTarget)
                otherTarget.RemoveLinked(target)

                AddMessage(string.format("Removed link from \"%s\" and \"%s\"", target.Name, otherTarget.Name), owner)
				links[item] = nil

                if SERVER then
                    -- lets send a net message to all clients so they remove our link
                    local msg = Networking.Start("lualinker.remove")
                    msg.WriteUInt16(UShort(target.ID))
                    msg.WriteUInt16(UShort(otherTarget.ID))
                    Networking.Send(msg)
                end

                return
            end
        end

        target.AddLinked(otherTarget)
        otherTarget.AddLinked(target)
        otherTarget.DisplaySideBySideWhenLinked = true
        target.DisplaySideBySideWhenLinked = true

        local text = string.format("Linked \"%s\" into \"%s\"", otherTarget.Name, target.Name)
        AddMessage(text, owner)

        if SERVER then
            -- lets send a net message to all clients so they add our link
            local msg = Networking.Start("lualinker.add")
            msg.WriteUInt16(UShort(target.ID))
            msg.WriteUInt16(UShort(otherTarget.ID))
            Networking.Send(msg)
        end

        links[item] = nil
    end
end)


if CLIENT then
    Networking.Receive("lualinker.add", function (msg)
        local target = Entity.FindEntityByID(msg.ReadUInt16())
        local otherTarget = Entity.FindEntityByID(msg.ReadUInt16())

        target.AddLinked(otherTarget)
        otherTarget.AddLinked(target)
        otherTarget.DisplaySideBySideWhenLinked = true
        target.DisplaySideBySideWhenLinked = true
    end)

    Networking.Receive("lualinker.remove", function (msg)
        local target = Entity.FindEntityByID(msg.ReadUInt16())
        local otherTarget = Entity.FindEntityByID(msg.ReadUInt16())

        target.RemoveLinked(otherTarget)
        otherTarget.RemoveLinked(target)
    end)
end