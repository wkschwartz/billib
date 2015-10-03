(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(custom-enabled-themes (quote (misterioso)))
 '(python-remove-cwd-from-path nil)
 '(python-shell-interpreter "python3")
 '(show-paren-mode t)
 '(uniquify-buffer-name-style (quote forward) nil (uniquify)))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

;; Play nice with Homebrew
(setq exec-path (append exec-path '("/usr/local/bin")))

;; set font size to 14pt gloablly
(set-face-attribute 'default nil :height 140)

;; Prevent Emacs.app from dinging annoyingly when I scroll to the end of the
;; buffer.
(setq ring-bell-function 'ignore)

;; python-mode hooks
(add-hook 'python-mode-hook (lambda () (setq python-indent 4)))

;; hooks for all programming modes
(add-hook 'prog-mode-hook 'auto-fill-mode)
(add-hook 'prog-mode-hook 'column-number-mode)
(add-hook 'prog-mode-hook 'linum-mode)
(add-hook 'prog-mode-hook
	  (lambda ()
	    (setq fill-column 80)
	    (setq indent-tabs-mode t)
	    (setq tab-width 4)
	    (setq show-trailing-whitespace t)))

;; yaml-mode stuff. See https://github.com/yoshiki/yaml-mode
(when (require 'yaml-mode nil :noerror)
  (add-to-list 'auto-mode-alist '("\\.yml$" . yaml-mode))
  (add-to-list 'auto-mode-alist '("\\.yaml$" . yaml-mode)))
;; go-mode stuff. See http://golang.org/misc/emacs/go-mode.el
(setq load-path (cons "/usr/local/Cellar/go/1.1.1/misc/emacs" load-path))
(when (require 'go-mode nil :noerror)
  (add-to-list 'auto-mode-alist '("\\.go$" . go-mode)))
(when (require 'csv-mode nil :noerror)
  (add-to-list 'auto-mode-alist '("\\.[Cc][Ss][Vv]\\'" . csv-mode))
  (autoload 'csv-mode "csv-mode"
	"Major mode for editing comma-separated value files." t))

;; Make Emacs have the recently-opened feature using the F7 key
(recentf-mode 1) ; keep a list of recently opened files
(global-set-key (kbd "<f7>") 'recentf-open-files)

;; For Django
(autoload 'django-html-mumamo-mode "~/.emacs.d/nxhtml/autostart.el")
(setq auto-mode-alist
      (append '(("\\.html?$" . django-html-mumamo-mode)) auto-mode-alist))
(setq mumamo-background-colors nil)
(add-to-list 'auto-mode-alist '("\\.html$" . django-html-mumamo-mode))

;; Homebrew told me to do this.
(let ((default-directory "/usr/local/share/emacs/site-lisp/"))
    (normal-top-level-add-subdirs-to-load-path))
