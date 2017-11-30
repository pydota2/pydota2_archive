-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

-- Atomic Actions
local actionGlyph           = require( GetScriptDirectory().."/actions/atomic_glyph" )
local actionLevelAbility    = require( GetScriptDirectory().."/actions/atomic_level_ability" )

-- Hero Functions
local actionNone            = require( GetScriptDirectory().."/actions/none" )
local actionClearAction     = require( GetScriptDirectory().."/actions/clear" )
local actionBuyback         = require( GetScriptDirectory().."/actions/buyback" )

--local actionMove            = require( GetScriptDirectory().."/actions/move_to_location" )
local actionMove            = require( GetScriptDirectory().."/actions/move_directly" )
local actionAttackUnit      = require( GetScriptDirectory().."/actions/attack_unit" )

local CmdProcessor = {}

LookUpTable = {
    ['0'] = actionGlyph,
    ['1'] = actionNone,
    ['2'] = actionClearAction,
    ['3'] = actionLevelAbility,
    ['4'] = actionMove,
    ['5'] = actionAttackUnit,
    ['6'] = actionBuyback,
}

function CmdProcessor:Run(hBot, tblActions)
    if table_length(tblActions) == 0 then
        dbg.myPrint("Got EMPTY tblActions")
        return
    end
    
    print_table(tblActions)
    
    for key, value in pairs(tblActions) do
        local cmd = LookUpTable[key]
        if cmd ~= nil then
            dbg.myPrint("Executing Action: ", cmd.Name)
            -- NOTE: It is assumed that the first argument (if args required)
            --       will be the handle to the bot, followed by arguments 
            --       provided by the `agent`.
            --       `Agent` args are double nested lists [[]], as some args
            --       specify a location for example so: [[-7000,-7000,128], [2]]
            --       to do a move_to_location (X,Y,Z) in Queued fashion
            if cmd.NumArgs == 2 then
                cmd:Call(hBot, value[1])
            elseif cmd.NumArgs == 3 then
                cmd:Call(hBot, value[1], value[2])
            elseif cmd.NumArgs == 0 then
                cmd:Call()
            elseif cmd.NumArgs == 1 then
                cmd:Call(hBot)
            elseif cmd.NumArgs == 4 then
                cmd:Call(hBot, value[1], value[2], value[3])
            else
                dbg.pause("Unimplemented number of Cmd Args for ", cmd.Name, ": ", cmd.NumArgs)
            end
        else
            dbg.myPrint("<ERROR> [", key, "] does not exist in action table!")
        end
    end
end

return CmdProcessor