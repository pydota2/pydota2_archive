-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
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
end

function DataPacket:ProcessPacket(key, reply)
    if DataPacket.LastPacket[key] then
        --dbg.myPrint("Got Reply Key: ", key)
        DataPacket.LastPacket[key].lastReply = reply
        DataPacket.LastPacket[key].processed = true
        DataPacket.LastPacket[key].reported = false
    else
        dbg.pause('Bad Reply Key:', key)
    end
end

function DataPacket:GetLastReply(key)
    if DataPacket.LastPacket[key] and not DataPacket.LastPacket[key].reported then
        DataPacket.LastPacket[key].reported = true
        return DataPacket.LastPacket[key].lastReply
    end
    return nil
end

return DataPacket
