---
title: "R in Doom Emacs"
author: "Yousuf Ali"
date: "2026-11-13"
categories: [R, emacs]
format: html
---

### Supercharging R Development in Doom Emacs: A Reproducible Setup

Emacs Speaks Statistics (ESS) is the undisputed champion for R development, but configuring it to feel modern and fluid can be a task. If you are using Doom Emacs, you get a pre-configured base, but specific workflows require specific tweaks.

Here is why the configuration below works and how to reproduce it step-by-step.

#### Why This Works

This configuration solves three specific pain points: **visual noise**, **process latency**, and **window chaos**.

1.  **Speeding Up Evaluation**: The line `(setq ess-eval-visibly 'nowait)` is crucial. By default, ESS waits for the R console to echo your code before returning control. This causes lag. `'nowait` sends the code to the inferior process instantly, keeping your editing flow uninterrupted.
2.  **Taming Window Management**: Doom Emacs uses `shackle` (via `set-popup-rules!`) to manage popups. ESS creates buffers like `*R*` (REPL) and `*help[R]*`. Without rules, these might steal your focus or split windows unpredictably. The rules defined here ensure the REPL sits neatly on the left and help buffers on the bottom, staying out of your way.
3.  **Aesthetic Cleanliness**: We enable `display-fill-column-indicator-mode` visually but disable `flymake` to prevent heavy linting from freezing large files. We also define `ess-indent-with-fancy-comments nil` to stop ESS from aggressively re-indenting standard comments, which often breaks the flow of writing roxygen2 documentation.

#### How to Set This Up (Reproducibly)

This setup requires a small modification to your Doom configuration.

**Step 1: Prerequisites**
Ensure you have the `ess` module enabled in your `init.el` or `packages.el`.

**Step 2: The Configuration**
Add the following to your `config.el` (or `~/.doom.d/config.el`). This isolates settings to load only when R is active, keeping your startup time fast.

```lisp
;; --- Core ESS Settings ---
(after! ess-r-mode
  ;; 1. Visuals
  (add-hook! 'ess-r-mode-hook #'display-fill-column-indicator-mode)
  (setq ess-eval-visibly 'nowait)           : Faster evaluation
  (setq ess-use-flymake nil)                : Disable heavy linting
  (setq ess-ask-for-ess-directory nil)      : Don't prompt for working dir
  (setq ess-indent-with-fancy-comments nil) : Cleaner indentation logic
  (setq ess-style 'RStudio-)                : Follow RStudio style guide

  ;; 2. Fontification (Syntax Highlighting)
  (setq ess-R-font-lock-keywords
        '((ess-R-fl-keyword:keywords . t)
          (ess-R-fl-keyword:constants . t)
          (ess-R-fl-keyword:modifiers . t)
          (ess-R-fl-keyword:fun-defs . t)
          (ess-R-fl-keyword:assign-ops . t)
          (ess-R-fl-keyword:%op% . t)
          (ess-fl-keyword:fun-calls . t)
          (ess-fl-keyword:numbers . t)
          (ess-fl-keyword:operators . t)
          (ess-fl-keyword:= . t)
          (ess-R-fl-keyword:F&T . t)))

  ;; 3. REPL Behavior
  (setq comint-move-point-for-output t)     : Auto-scroll REPL
  (add-hook! 'inferior-ess-mode-hook
    (lambda () (setq ansi-color-for-comint-mode 'filter)))
  (add-hook 'inferior-ess-mode-hook #'doom-mark-buffer-as-real-h)

  ;; 4. Window Layouts (Popup Rules)
  (set-popup-rules!
    '(("*R$" :side left :height 1 :width .5)   : Main REPL on left
      ("^R:" :side right :height 1 :width .5)  : Secondary windows
      ("*help" :side bottom :height .5 :width .5)))) : Help docs on bottom

;; --- Keybindings ---
(map! :after ess
      :map ess-r-mode-map
      :n [C-return] #'ess-eval-region-or-line-and-step
      :localleader
      :prefix "e"
      :n "s" #'ess-switch-process
      :n "r" #'ess-interrupt
      :n "e" #'run-ess-r)

;; Markdown/RMarkdown settings
(setq markdown-code-block-braces t)
```

**Step 3: Apply Changes**
Run `M-x doom/reload` or restart Emacs. Open an R file, hit `C-return` to send a line, and watch it execute instantly in a stable, dedicated side window.
