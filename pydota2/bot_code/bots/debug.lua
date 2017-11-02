-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
-------------------------------------------------------------------------------

local X = {}

function X.myPrint(...)
    local args = {...}
    
    if #args > 0 then
        local hBot = GetBot()
        local botname = "<UNKNOWN>"

        if hBot then
            if hBot.myBot then
                botname = GetBot().mybot.Name
            else
                botname = hBot:GetUnitName()
            end
        end

        local msg = tostring(Round(GameTime(), 5)).." [" .. botname .. "]: "
        for i,v in ipairs(args) do
            msg = msg .. tostring(v)
        end
        
        --uncomment to only see messages by bots mentioned underneath
        --if botname == "invoker" then --or botname == "viper" then
            if string.len(msg) > 8000 then
                print('[LEN]: ', string.len(msg), ' :: ', msg)
            else
                print(msg)
            end
        --end
    end
end

function X.pause(...)
    X.myPrint(...)
    DebugPause()
end

local last_draw_time = -500

local bot_states = {}

local LINE_HEIGHT = 10
local TITLE_VALUE_DELTA_X = 10

local BOT_STATES_MAX_LINES = 2
local BOT_STATES_X = 1600
local BOT_STATES_Y = 100

local function SetBotState(name, line, text)
    if line < 1 or BOT_STATES_MAX_LINES > 2 then
        print("SetBotState: line out of bounds!")
        return
    end
    if bot_states[name] == nil then
        bot_states[name] = {}
    end
    bot_states[name][line] = text
end

local function updateBotStates()
    local listAllies = GetUnitList(UNIT_LIST_ALLIED_HEROES)
    for _, ally in pairs(listAllies) do
        if ally:IsBot() and not ally:IsIllusion() and ally.SelfRef then
            local hMyBot = ally.SelfRef
            local mode = hMyBot:getCurrentMode()
            local state = mode:GetName()
            SetBotState(hMyBot.Name, 1, state)
        end
    end
end

function X.draw()
    if last_draw_time > GameTime() - 0.010 then return end
    last_draw_time = GameTime()

    updateBotStates()
    
    local y = BOT_STATES_Y
    for name, v in pairs(bot_states) do
        DebugDrawText( BOT_STATES_X, y, name, 255, 0, 0 )
        for line,text in pairs(v) do
            DebugDrawText( BOT_STATES_X + TITLE_VALUE_DELTA_X, y + line * LINE_HEIGHT, text, 255, 0, 0 )
        end
        y = y + (BOT_STATES_MAX_LINES + 1) * LINE_HEIGHT
    end
end

function X.DebugStats()
    DebugDrawText(25, 50, "LH/D = "..GetBot():GetLastHits().."/"..GetBot():GetDenies(), 255, 255, 255);
end

return X
