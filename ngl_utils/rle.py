#!/usr/bin/env python3

# ------------------------------------------------------------------------------
# rlem_encode
# ------------------------------------------------------------------------------
def rlem_encode(data):
    count = 1       # count words
    index = 0
    start_index = 0    
    out_list = []   # out RLEm compressed list
    
    # init state
    if data[0] != data[1]:                
        state = 'mismatch'
    else:
        state = 'match'

    data_len = len( data )    
    for index in range( data_len - 3 ):
        
        if state == 'match':
            
            if data[ index ] == data[ index+1 ] and index < data_len - 4:
                count += 1                
            else:
                out_list.append( count )
                out_list.append( data[index] )                
                
                if data[ index+1 ] != data[ index+2 ]:
                    state = 'mismatch'

                start_index = index + 1
                count = 1         

        elif state == 'mismatch':
            
            odta = data[ start_index:index+1 ]

            if data[ index ] != data[ index+1 ] and index < data_len - 4:
                
                if data[ index+1 ] == data[ index+2 ]:                   
                    out_list.append( 0x8000 | count )
                    out_list += [ word for word in odta ]
                    state = 'match'
                    count = 1
                else:
                    count += 1
            else:                
                if count > 1:                    
                    out_list.append( 0x8000 | count )
                    out_list += [ word for word in odta ]
                
                if data[index+1] == data[index+2]:
                    state = 'match'
                start_index = index + 1
                count = 1       

    out_list.append( 0x8000 | len(data[start_index:]) )       
    out_list += [ word for word in data[start_index:] ] 
    
    return out_list

# ------------------------------------------------------------------------------
# rlem_decode
# ------------------------------------------------------------------------------ 
def rlem_decode(data):
    out_list = []   # out decompressed list

    data_len = len( data )
    index = 0

    while index < data_len - 3:
        # print(index, data[index])
        word = int( data[index] )
        
        if word & 0x8000:
            cnt = word & ~0x8000
            for w in range(cnt):
                index += 1
                out_list.append( data[index] )
            index += 1
        else:
            cnt = word
            for w in range(cnt):                
                out_list.append( data[index+1] )
            index += 2
    
    if type(out_list[1]) == type(str):
        out_list = ''.join( out_list )

    return out_list