-------------------------------------------------------------------------------
--- AUTHOR: Nostrademous
--- GITHUB REPO: https://github.com/pydota2
-------------------------------------------------------------------------------

dkjson = require( "game/dkjson" )

local dbg = require( GetScriptDirectory().."/debug" )
local web_config = require( GetScriptDirectory().."/web_config" )
local packet = require( GetScriptDirectory().."/data_packet" )

local webserver = {}

local webserverFound         = false
local webserverAuthTried     = false

webserver.startTime         = -1000.0
webserver.lastPollPacket    = -1000.0
webserver.lastReply         = nil

function webserver.SendPacket( json )    
    -- for RADIANT port will be 2222, for DIRE 2223
    local ip_addr = web_config.IP_ADDR .. ":" .. tostring(web_config.IP_BASE_PORT + GetTeam())
    -- print("CreateRemoteHTTPRequest: " .. ip_addr)
    local req = CreateRemoteHTTPRequest( ip_addr )
    req:SetHTTPRequestRawPostBody("application/json", json)
    req:Send( function( result )
        for k,v in pairs( result ) do
            if k == "Body" then
                local jsonReply, pos, err = dkjson.decode(v, 1, nil)
                if err then
                    print("JSON Decode Error: ", err)
                    print("Sent Message: ", json)
                    print("Msg Body: ", v)
                else
                    --print( tostring(jsonReply) )
                    packet:ProcessPacket(jsonReply.Type, jsonReply)
                    
                    if jsonReply.Type == packet.TYPE_AUTH then
                        webserverFound = true
                        print("Connected Successfully to Backend Server")
                    elseif jsonReply.Type == packet.TYPE_POLL then
                        print("Received Update from Server")
                    end
                end
                --break
            end
        end
    end )
end

function webserver.SendData(hBot)
    -- if we have not verified the presence of a webserver yet, send authentication packet
    if not webserverFound and not webserverAuthTried then
        webserverAuthTried = true
        local jsonData = webserver.CreateAuthPacket()
        packet:CreatePacket(packet.TYPE_AUTH, jsonData)
        dbg.myPrint("SENDING AUTHENTICATION REQUEST")
        webserver.SendPacket(jsonData)
    end
    
    -- if we have a webserver
    if webserverFound then
        if packet.LastPacket[packet.TYPE_POLL] == nil or (packet.LastPacket[packet.TYPE_POLL].processed
            and (GameTime() - webserver.lastPollPacket) > 0.1) then
            local jsonData = webserver.CreatePollPacket(hBot)
            packet:CreatePacket(packet.TYPE_POLL, jsonData)
            webserver.lastPollPacket = GameTime()
            dbg.myPrint("SENDING POLL REQUEST")
            webserver.SendPacket(jsonData)
        end
    end
end

function webserver.CreateAuthPacket()
    local json = {}
    
    json.Type = packet.TYPE_AUTH
    json.Time = RealTime()
    
    return dkjson.encode(json)
end

function webserver.CreatePollPacket(hBot)
    local json = {}
    
    json.Type = packet.TYPE_POLL
    json.Time = RealTime()
    
    for pid = 1,5,1 do
        hHero = GetTeamMember(pid)
        if hHero.rtt then
            json[tostring(hHero:GetPlayerID())] = hHero.rtt
        end
    end
    
    return dkjson.encode(json)
end

function webserver.GetLastReply(sType, pID)
    return packet:GetLastReply(sType, pID)
end

return webserver

