-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local ActionClear = {}

ActionClear.Name = "Clear Action"
ActionClear.NumArgs = 2

-------------------------------------------------

function ActionClear:Call(hHero, bStop)
    --print_table(bStop)
    --dbg.myPrint("Changing: '", bStop[1], "' to '", toboolean(bStop[1]), "'")
    hHero:Action_ClearActions(toboolean(bStop[1]))
end

-------------------------------------------------

return ActionClear