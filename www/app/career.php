<?php

//
// Controller for display
// https://{domain}/career/career
//
class Career extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(15);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'career');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/career/research
//
class Research extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(16);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'research');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/career/lecture
//
class Lecture extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(17);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'lecture');
        $module->run();
    }

}

//
// Controller for display
// https://{domain}/career/publication
//
class Publication extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(18);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make()
    {
        $this->module();
    }

    public function module()
    {
        $module = new \Module\Contents\Make_Controller();
        $module->set('key', 'publication');
        $module->run();
    }

}
