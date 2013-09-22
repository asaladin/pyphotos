<%inherit file="base.mako" />




<div class='hero-unit'>
<h2>album: ${albumname}</h2>
</div>

%if owner.email == username:
<a href="addphoto">Add a new photo</a>
<a href="/createticket/${albumname}">Inviter quelqu'un</a>
%endif

%for photo in photos: 

    <div class="albumcontainer">
        <a href="${request.route_url('fullsize', albumname=photo.album.name, filename=photo.filename)}"> 
            <img src="${photo.thumbnailpath}" /><br/>
         ${photo.filename} 
        </a> 
    </div><!--/span4-->

%endfor



