-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local MoveDirectly = {}

MoveDirectly.Name = "Move Directly to Location"
MoveDirectly.NumArgs = 3

-------------------------------------------------

ABILITY_STANDARD    = 0
ABILITY_PUSH        = 1
ABILITY_QUEUE       = 2

function MoveDirectly:Call( hUnit, vLoc, iType )
    if not hUnit:IsAlive() or hUnit:IsRooted() or hUnit:IsStunned() then
        dbg.pause("[ERROR] - MoveDirectly under death/root/stun")
        return
    end
    
    --dbg.myPrint("Moving to: <", vLoc[1],", " vLoc[2], "> from <", hUnit:GetLocation().x, ", ", hUnit:GetLocation().y, ">")
    
    iType = iType[1]
    
    vLoc = Vector(vLoc[1], vLoc[2], vLoc[3])
    DebugDrawCircle(vLoc, 25, 255, 255 ,255)
    DebugDrawLine(hUnit:GetLocation(), vLoc, 255, 255, 255)
    
    if iType == nil or iType == ABILITY_STANDARD then
        hUnit:Action_MoveDirectly(vLoc)
    elseif iType == ABILITY_PUSH then
        hUnit:ActionPush_MoveDirectly(vLoc)
    elseif iType == ABILITY_QUEUE then
        hUnit:ActionQueue_MoveDirectly(vLoc)
    else
        dbg.pause("[ERROR] - Unknown iType: ", iType)
    end
end

-------------------------------------------------

return MoveDirectly