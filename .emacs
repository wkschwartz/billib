(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(custom-enabled-themes (quote (misterioso)))
 '(uniquify-buffer-name-style (quote forward) nil (uniquify))
 '(python-remove-cwd-from-path nil)
 '(show-paren-mode t)
 '(initial-buffer-choice t))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

;; python-mode hooks
(add-hook 'python-mode-hook 'auto-fill-mode)
(add-hook 'python-mode-hook 'column-number-mode)
(add-hook 'python-mode-hook 'linum-mode)
(add-hook 'python-mode-hook
	  (lambda ()
	    (setq flyspell-issue-message-flag nil)
	    (flyspell-prog-mode)
	    (setq fill-column 79)
	    (setq indent-tabs-mode t)
	    (setq tab-width 4)
	    (setq python-indent 4)
	    (setq show-trailing-whitespace t)))

;; yaml-mode stuff. See https://github.com/yoshiki/yaml-mode
(when (require 'yaml-mode nil :noerror)
  (add-to-list 'auto-mode-alist '("\\.yml$" . yaml-mode))
  (add-to-list 'auto-mode-alist '("\\.yaml$" . yaml-mode)))
