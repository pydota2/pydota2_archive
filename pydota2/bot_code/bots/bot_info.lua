-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local BotInfo = {}

--------------------------------------------------------

function BotInfo:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    return o
end

--[[
function BotInfo:Init()
end
--]]

--------------------------------------------------------

return BotInfo
