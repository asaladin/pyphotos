<%inherit file="base.mako" />




<div class='hero-unit'>
<h2>album: ${albumname}</h2>
</div>

%if owner.email == username:
<a href="addphoto">Add a new photo</a>
<a href="/createticket/${albumname}">Inviter quelqu'un</a>
%endif



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
           <a href="${request.route_url('fullsize', albumname=photo.album.name, filename=photo.filekey)}"> 
               <img src="${photo.thumbnailpath}" />  ${photo.filekey} 
           </a> 
        </div><!--/span4-->
        %endif
    %endfor

</div><!--/row-->
%endfor




