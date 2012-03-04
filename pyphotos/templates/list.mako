<%inherit file="base.mako" />


<div class='hero-unit'>
<h2>album: ${albumname}</h2>
</div>

<a href="addphoto">Ajouter une photo</a>
<a href="/createticket/${albumname}">Inviter quelqu'un</a>


<% 
from itertools import izip_longest
def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)
%>


%for photo1,photo2 in grouper(2 , photos):
<div class="row-fluid">
    <div class="span4">
       <a href="${photo1['url']}"> 
          <img src="/thumbnail?filename=${photo1['filename']}" />  ${photo1['filename']} 
       </a> 
    </div><!--/span-->


    <div class="span4">
       <a href="${photo2['url']}"> 
          <img src="/thumbnail?filename=${photo2['filename']}" />  ${photo2['filename']} 
       </a> 
    </div><!--/span-->

</div><!--/row-->
%endfor




