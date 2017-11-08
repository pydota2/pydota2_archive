-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

--- LOAD OUR GLOBAL CONSTANTS

--- LOAD OUR HELPERS
dbg = require( GetScriptDirectory().."/debug" )

local packet = require( GetScriptDirectory().."/data_packet" )
local server = require( GetScriptDirectory().."/webserver_out" )

local THROTTLE_RATE = 0.25   -- in seconds (0.1 == 10 times per second)

local X = {}
X.lastUpdateTime = -1000.0

function X:new()
    local mybot = {}
    setmetatable(mybot, self)
    self.__index = self
    
    -- TODO - other stats we want to track?
    
    GetBot().mybot = mybot     -- make mybot accessible anywhere after calling GetBot()
    
    return mybot
end

local function ServerUpdate()
    local hBot = GetBot()
    
    -- send our POLL to webserver to receive instructions back
    -- or our authentication packet if first time sending
    server.SendData(hBot)

    local serverReply = server.GetLastReply(packet.TYPE_POLL)
    if serverReply ~= nil then
        dbg.myPrint("Need to Process new Server Reply")
        if serverReply.status == 200 then
            dbg.myPrint("Packet RTT: ", RealTime() - serverReply.Time)
            dbg.myPrint("Server Data: ", serverReply.Data)
        else
            dbg.myPrint("Server Error: ", serverReply.Data)
        end
    end

    return nil, BOT_MODE_DESIRE_NONE
end

function X:Think(hBot)
    -- if we are a human player, don't bother
    if not hBot:IsBot() then return end

    if not self.Init then
        self:DoInit(hBot)
        return
    end

    if GetGameState() ~= GAME_STATE_GAME_IN_PROGRESS and GetGameState() ~= GAME_STATE_PRE_GAME then return end

    -- draw debug info to Game UI
    --dbg.draw()

    -- throttle how often we query the back-end server
    if (GameTime() - X.lastUpdateTime) >= THROTTLE_RATE then
        -- check if bot has updated directives from our AI
        dbg.myPrint("SENDING SERVER UPDATE")
        local highestDesiredMode, highestDesiredValue = ServerUpdate()
        X.lastUpdateTime = GameTime()
    end
end

function X:DoInit(hBot)
    --if not globalInit then
    --    InitializeGlobalVars()
    --end

    self.Init = true
    hBot.mybot = self

    local fullName = hBot:GetUnitName()
    self.Name = string.sub(fullName, 15, string.len(fullName))
end

return X

