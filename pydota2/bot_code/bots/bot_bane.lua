-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local controller = require( GetScriptDirectory().."/controller" )
local heroes = require(GetScriptDirectory().."/heroes/_heroes")

local bot = controller:new(heroes:GetHero())

function bot:new(o)
    o = o or controller:new(o)
    setmetatable(o, self)
    self.__index = self
    return o
end

local myBot = bot:new{}

function Think()
    local hBot = GetBot()
    
    myBot:Think( hBot )
end

