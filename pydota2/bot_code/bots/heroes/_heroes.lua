-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local Heroes = {}

--------------------------------------

function Heroes:GetHero()
    local hero_name = GetUnitName(GetBot())
    local required = require(GetScriptDirectory().."/heroes/"..hero_name)
    return required:new()
end

--------------------------------------

return Heroes
