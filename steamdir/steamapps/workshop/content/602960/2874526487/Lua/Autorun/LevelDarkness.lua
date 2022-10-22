Hook.Add("roundStart", "make level dark", function()
    local parameters = Level.Loaded.LevelData.GenerationParams

    parameters.AmbientLightColor = Color(0, 0, 0, 0)
end)