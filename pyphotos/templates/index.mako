<%inherit file="base.mako" />


<h3>List of albums </h3>

%for a in albums:
    <div style='margin-bottom: 30px; margin-right:40px; float:left;'>
      <a href="/album/${a.name}/list"><img src='${a.cover.thumbnailpath}' /><br />
      ${a.name} (${len(a.photos)})</a>
    </div>
%endfor



