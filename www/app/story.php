<?php

//
// Controller for display
// https://{domain}/story/sports-video
//
class Sports_video extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(24);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'story_sports_video');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/story/basketball
//
class Basketball extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(25);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'story_basketball');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/story/boxing
//
class Boxing extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(26);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'story_boxing');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/story/album
//
class Album extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(27);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'story_album');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/story/family
//
class Family extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(28);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'story_family');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/story/julye
//
class Julye extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(29);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'story_julye');
        $module->run();
    }

}
