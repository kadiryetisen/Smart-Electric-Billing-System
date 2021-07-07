import os 
import cv2                                                                                                                                    
import numpy as np                                                              
import sys                                                                   
import pytesseract                                                         

pytesseract.pytesseract.tesseract_cmd  = r".\Tesseract-OCR\tesseract.exe"   



def ocr_image(img):                                                                                                      
    
    gry_disp_arr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                                                                 
    kernel = np.ones((1,1),np.uint8)                                                                                    
    kernel2 = np.ones((5,5),np.uint8)                                                                                    
    thresh=cv2.adaptiveThreshold(gry_disp_arr,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)                                                                                  
 
    dst = cv2.medianBlur(thresh,9)                                                                                     
    dilation = cv2.dilate(dst,kernel,iterations = 1)                                                                

    
    height, width = dilation.shape[:2]                                                                                   

    imm = dilation[int(0.12*height):int(0.12*height+0.47*height), int(0.168*width):int(0.168*width+0.8*width)]               
    imm = cv2.erode(imm,kernel2,iterations = 1)                                                                                

    cv2.imshow("son", imm)                                                                                                  
    cv2.waitKey(0)                                                                                                              

    result = pytesseract.image_to_string(imm, lang="ssd",\
         config="--psm 7 -c tessedit_char_whitelist=.0123456789")                                                                      
    
    result = result[:result.index("\n")]                                                                                                    
    

    if "." in result:
        pass
    else:
        result = result[:-3] + "." + result[-3:]                                                                                            
    
    
    return int(result[-3:])                                                                                                              



def find_display(img_path): 
    
    _width  = 600.0
    _height = 420.0
    _margin = 0.0

    corners = np.array(
        [
            [[  		_margin, _margin 			]],
            [[ 			_margin, _height + _margin  ]],
            [[ _width + _margin, _height + _margin  ]],
            [[ _width + _margin, _margin 			]],
        ]
    )   

    
    pts_dst = np.array( corners, np.float32 ) 

    rgb = cv2.imread(img_path) 
    
    gray = cv2.cvtColor( rgb, cv2.COLOR_BGR2GRAY ) 

    
    
    
    
    
    gray = cv2.bilateralFilter( gray, 1, 10, 120 ) 

    edges  = cv2.Canny( gray, 10, 250 ) 

    kernel = cv2.getStructuringElement( cv2.MORPH_RECT, ( 7, 7 ) ) 

    closed = cv2.morphologyEx( edges, cv2.MORPH_CLOSE, kernel ) 

    contours, h = cv2.findContours( closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE ) 
   
    empty = [0]     

    aaa = 0 
    for cont in contours:

        
        if cv2.contourArea( cont ) > 5000 :
            arc_len = cv2.arcLength( cont, True ) 
            approx = cv2.approxPolyDP( cont, 0.1 * arc_len, True)                                                
            
            if ( len( approx ) == 4 ):                                                                     
                area = cv2.contourArea(cont)                                                                           
                if (area > empty[0]): 
                    empty[0] = area            
                                                                                
                    aaa = cont

    cont = aaa 

    arc_len = cv2.arcLength( cont, True ) 

    approx = cv2.approxPolyDP( cont, 0.1 * arc_len, True ) 

    if ( len( approx ) == 4 ):                                                                          
      
        pts_src = np.array( approx, np.float32 )

        h, status = cv2.findHomography( pts_src, pts_dst )
        out = cv2.warpPerspective( rgb, h, ( int( _width + _margin * 2 ), int( _height + _margin * 2 ) ) )

        cv2.drawContours(rgb, [approx], -1, ( 255, 0, 0 ), 2 ) 
        cv2.waitKey(0)    

    cropped = rgb[approx.ravel()[3]:approx.ravel()[5], approx.ravel()[2]:approx.ravel()[0]] 


    return cropped 



if __name__ == "__main__": #

    results = []
    for i in os.listdir("photos"): 
        if i.endswith("jpeg") or i.endswith("jpg") or i.endswith("png"):
            cropped = find_display(os.path.join("photos", i))
            result = ocr_image(cropped)

            results.append(result) 

    results = sorted(results)
    kw_number = results[-1] - results[-2]
    print("for ", kw_number, "kW;") 
    
    fiyat = 0 
    aktif_enerji =0 
    enerji_fonu = 0 
    trt_payi = 0 
    belediye_tuketim_vergisi = 0 
    katma_deger_vergisi = 0 
    aktif_enerji = (239.033/395.033) * (kw_number/1000)
    enerji_fonu = (1.55/395.033) * (kw_number/1000)  
    trt_payi = (3.10/395.033) * (kw_number/1000)  
    belediye_tuketim_vergisi = (7.76/395.033) * (kw_number/1000)  
    katma_deger_vergisi = (45.26/395.033) * (kw_number/1000)

    fiyat = aktif_enerji + enerji_fonu + trt_payi + belediye_tuketim_vergisi + katma_deger_vergisi 
    fiyat = round(fiyat,3)
    print("Your electric bill is ",fiyat, "£")
    print("You can change tax ratio on 138-150")

