finish  
/clear,nostart  
    
/out,spm,out
*vwrite, ' ', 'load','boom-A','jib-A', 'reach-X', 'reach-Z', 'fbmax', 'fbmin', 'fbbuc', 'fjmax', 'fjmin', 'fjbuc'   
(A1, 11A8)  
*vwrite, ' ', 't', 'deg', 'deg', 'mm', 'mm', '-', '-', '-', '-', '-', '-'   
(A1,11A8)   
/out
    
! *dim,ufnames,char,6   
! ufnames(1) =  'fbmax', 'fbmin', 'fbbuc', 'fjmax', 'fjmin', 'fjbuc'
    
/out,spmbubble,out  
*vwrite, ' ', 'load', 'alpha', 'beta', ',', 'reach-X', 'reach-Z', 'UF-name', 'UF-value' 
(A1, 8A8)   
/out
    
    
*do,liveload,3,7,2  
  *if,liveload,eq,7,then ! scraping by to do 3, 5 and 10 tons   
  liveload = 10 
  *endif
  *do,alpha,0,81.7,5
    *do,beta,0,120,5 ! 180 is stretched, it's the construction angle
      finish
      parsav
      /clear,nostart
      /view,,,-1,   
      parres
      /input,spmB,mac,,:module  
      /input,spmC,mac   
    *enddo  
  *enddo
*enddo  
