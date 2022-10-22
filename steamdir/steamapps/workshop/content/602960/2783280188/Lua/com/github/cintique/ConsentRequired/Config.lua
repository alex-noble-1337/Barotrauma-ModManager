-- User edited configuration file.

local Environment = require 'com.github.cintique.ConsentRequired.Util.Environment'

local _ENV = Environment.PrepareEnvironment(_ENV)


--------- Start editing here ---------

AffectedItems = {
  -- Neurotrauma
  "surgerysaw",           -- Surgical saw (amputations)
  "organscalpel_liver",   -- Organ procurement scalpel: liver
  "organscalpel_lungs",   -- Organ procurement scalpel: lungs
  "organscalpel_kidneys", -- Organ procurement scalpel: kidneys
  "organscalpel_heart",   -- Organ procurement scalpel: heart
  "organscalpel_brain",   -- Organ procurement scalpel: brain
  "emptybloodpack",       -- Empty blood bag (takes blood)
  -- NeuroEyes
  "organscalpel_eyes",    -- Organ procurement scalpel: eyes
}

--------- Stop editing here ---------

return Environment.Export(_ENV)
