-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local Heroes = {}

--------------------------------------

local function GetUnitName( hUnit )
    local sName = hUnit:GetUnitName()
    return string.sub(sName, 15, string.len(sName))
end

function Heroes:GetHero()
    local hero_name = GetUnitName(GetBot())
    local required = require(GetScriptDirectory().."/heroes/"..hero_name)
    return required:new()
end

--------------------------------------

return Heroes
