Hook.Add("roundStart", "make hulls dark", function()
   for k, hull in pairs(Hull.HullList) do
      hull.AmbientLight = Color(0, 0, 0, 0)
   end
end)