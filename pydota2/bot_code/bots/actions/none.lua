-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local ActionNone = {}

ActionNone.Name = "No Action"
ActionNone.NumArgs = 0

-------------------------------------------------

function ActionNone:Call()
    dbg.myPrint("No Action")
end

-------------------------------------------------

return ActionNone