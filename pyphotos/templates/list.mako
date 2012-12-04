<%inherit file="base.mako" />

<%def name='generate(url)' >
   %if "/thumbnail/generate/" in url:
   ${url}
   %else:
   ${request.s3.generate_url(3600 , "GET" ,'asphotos', url )}
   %endif
</%def>


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


%for group_photo in grouper(2 , photos):
<div class="row-fluid">
    %for photo in group_photo:
    %if photo is not None:
    <div class="span4">
       <a href="${request.route_url('fullsize', albumname=photo.albumname, filename=photo.filename)}"> 
          <img src="${generate(photo.thumbnailpath)}" />  ${photo.filename} 
       </a> 
    </div><!--/span-->
    %endif
    %endfor

</div><!--/row-->
%endfor




