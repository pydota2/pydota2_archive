-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local MoveToLocation = {}

MoveToLocation.Name = "Move to Location"
MoveToLocation.NumArgs = 3

-------------------------------------------------

function MoveToLocation:Call( hUnit, vLoc, iType )
    vLoc = Vector(vLoc[1], vLoc[2], vLoc[3])
    DebugDrawCircle(vLoc, 25, 255, 255 ,255)
    DebugDrawLine(hUnit:GetLocation(), vLoc, 255, 255, 255)
    
    if iType == nil or iType == ABILITY_STANDARD then
        hUnit:Action_MoveToLocation(vLoc)
    elseif iType == ABILITY_PUSH then
        hUnit:ActionPush_MoveToLocation(vLoc)
    elseif iType == ABILITY_QUEUE then
        hUnit:ActionQueue_MoveToLocation(vLoc)
    end
end

-------------------------------------------------

return MoveToLocation