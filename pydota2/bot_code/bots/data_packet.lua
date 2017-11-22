-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

local dbg = require( GetScriptDirectory().."/debug" )

local DataPacket = {}

DataPacket.LastPacket = {}

DataPacket.TYPE_AUTH    = "X"
DataPacket.TYPE_POLL    = "P"

function DataPacket:CreatePacket(key, packet)
    --local seq = Round(RealTime(), 3) * 1000

    if not DataPacket.LastPacket[key] then
        DataPacket.LastPacket[key] = {}
    end

    --DataPacket.LastPacket[key].seq = seq
    DataPacket.LastPacket[key].lastSent = packet
    DataPacket.LastPacket[key].processed = false
    DataPacket.LastPacket[key].reported = {}
end

function DataPacket:ProcessPacket(key, reply)
    if DataPacket.LastPacket[key] then
        --dbg.myPrint("Got Reply Key: ", key)
        DataPacket.LastPacket[key].lastReply = reply
        DataPacket.LastPacket[key].processed = true
    else
        dbg.pause('Bad Reply Key:', key)
    end
end

function DataPacket:GetLastReply(key, pID)
    if DataPacket.LastPacket[key] and not DataPacket.LastPacket[key].reported[pID] then
        DataPacket.LastPacket[key].reported[pID] = true
        if pID == 0 then
            dbg.myPrint("Getting Last TEAM Packet Reply")
        else
            dbg.myPrint("Getting MY Last Packet Reply")
        end
        return DataPacket.LastPacket[key].lastReply
    end
    return nil
end

return DataPacket
