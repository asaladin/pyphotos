<%inherit file="base.mako" />


<h3>List of albums </h3>
<ul>
%for a in albums:
    <li><a href="/album/${a['title']}/list">${a['title']}</a></li>
%endfor
</ul>

<br />
<form method='post' action='/import/s3'>
albumname: <input type='text' name='albumname' /> <br />
directory: <input type='text' name='dirname' /> <br />
visible: <input type='checkbox' name='visible' checked='true' />
<button action='submit'>Submit</button>
</form>


