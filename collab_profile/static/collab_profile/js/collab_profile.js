// set textareas ckeditor should attach to
CKEDITOR.replaceClass='CKEditor';

var activateMarkdown = function() {
    CKEDITOR.instances[contentSelector].setMode('markdown')
};

var activateWysiwyg = function() {
    CKEDITOR.instances[contentSelector].setMode('wysiwyg')
};

var contentSelector = 'id_description'

/*
	CKEditor expects html as input, so we frontrun it a bit
	by converting the textarea markdown content first
*/

var initialMarkdown = $('#'+contentSelector).html()
console.log(initialMarkdown)
$.getScript(CKEDITOR.basePath + 'plugins/markdown/js/marked.js', function() {
	$('#'+contentSelector).html(marked(initialMarkdown, {langPrefix: 'language-'}));
	console.log(marked(initialMarkdown, {langPrefix: 'language-'}))
	console.log($('#'+contentSelector).html())
});

/*
  The CKEditor plugin lazyloads the markdown converter on demand.
  We explicitly load all scripts now to ensure markdown conversion is
  complete on page save.
*/
CKEDITOR.on('instanceCreated', function() {
	CKEDITOR.scriptLoader.load(CKEDITOR.basePath + 'plugins/markdown/js/to-markdown.js')
	CKEDITOR.document.appendStyleSheet(CKEDITOR.basePath + 'plugins/markdown/css/codemirror.min.css');
	CKEDITOR.scriptLoader.load(CKEDITOR.basePath + 'plugins/markdown/js/codemirror-gfm-min.js')
});


var prepareSave = function(selector) {
	$(selector).on('click', function(ev) {
        activateMarkdown();
    });
}

// profile form
if ($('#edit-profile').length) {

	var formSelector = 'edit-profile';
    var saveButtonSelector = '#'+formSelector+' button[type="submit"]'
	prepareSave(saveButtonSelector);
}

