<%inherit file="base.mako" />




<div class='hero-unit'>
<h2>album: ${albumname}</h2>
</div>

<a href="addphoto">Ajouter une photo</a>
##<a href="/createticket/${albumname}">Inviter quelqu'un</a>


<% 
from itertools import izip_longest
def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)
%>


%for group_photo in grouper(2 , photos):
<div class="row-fluid">
    %for photo in group_photo:
    %if photo is not None:
    <div class="span4">
       <a href="${request.route_url('fullsize', albumname=photo.albumname, filename=photo.filename)}"> 
          <img src="${photo.thumbnailpath}" />  ${photo.filename} 
       </a> 
    </div><!--/span-->
    %endif
    %endfor

</div><!--/row-->
%endfor




