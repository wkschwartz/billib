(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(custom-enabled-themes (quote (misterioso)))
 '(uniquify-buffer-name-style (quote forward) nil (uniquify))
 '(python-remove-cwd-from-path nil)
 '(show-paren-mode t))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

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
(when (require 'go-mode nil :noerror)
  (add-to-list 'auto-mode-alist '("\\.go$" . go-mode)))

;; Make Emacs have the recently-opened feature using the F7 key
(recentf-mode 1) ; keep a list of recently opened files
(global-set-key (kbd "<f7>") 'recentf-open-files)
