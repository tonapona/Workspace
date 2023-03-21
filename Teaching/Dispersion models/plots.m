clc;
clear;

xp=1e3;
x=linspace(1e0,1e4,1e6);
y=8.85*1e-12*(1-(xp./x).^2);

figure
semilogx(x,y)
grid on

xl=xline(xp,'--','$\omega_p$','Interpreter','latex','FontSize',16);
xl.LabelVerticalAlignment='bottom';

xlabel('$\omega$ $\left[ \mathrm{Hz} \right]$','Interpreter','latex','FontSize',20)
ylabel('$\epsilon$ $\left[ \mathrm{F} \cdot \mathrm{m}^{-1} \right]$','Interpreter','latex','FontSize',20)